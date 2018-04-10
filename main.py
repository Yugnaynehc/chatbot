#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2016-12-08 10:56:55
# @Author  : He Liang (helianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

import os
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from msgList import MsgList
from flowlayout import FlowLayout
from Seq2Seq import chat
from speech import recog
from record import record


HEAD1 = 'icons/head3.jpg'
HEAD2 = 'icons/head2.jpg'


class TextEdit(QTextEdit, QObject):
    '''支持ctrl+return信号发射的QTextEdit'''
    entered = pyqtSignal()

    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent)

    def keyPressEvent(self, e):
        # print e.key() == Qt.Key_Return,e.key() == Qt.Key_Enter, e.modifiers() == Qt.ControlModifier
        # if (e.key() == Qt.Key_Return) and (e.modifiers() == Qt.ControlModifier):
        #     self.entered.emit()  # ctrl+return 输入
        if e.key() == Qt.Key_Return:
            self.entered.emit()  # return 输入
            self.clear()
        super(TextEdit, self).keyPressEvent(e)


class MsgInput(QWidget, QObject):
    '''自定义的内容输入控件，支持图像和文字的输入，文字输入按回车确认。'''
    textEntered = pyqtSignal(str)

    btnSize = 35
    teditHeight = 100

    def __init__(self, parent=None):
        super(MsgInput, self).__init__(parent)
        self.setContentsMargins(3, 3, 3, 3)

        self.textEdit = TextEdit()
        self.textEdit.setMaximumHeight(self.teditHeight)
        self.setMaximumHeight(self.teditHeight + self.btnSize)
        self.textEdit.setFont(QFont("Times", 15, QFont.Normal))
        self.textEdit.entered.connect(self.sendText)

        sendTxt = QPushButton(u'发送')
        sendTxt.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        sendTxt.setFixedHeight(self.btnSize)
        sendTxt.clicked.connect(self.sendText)

        sendSound = QPushButton(u'录音')
        sendSound.setFont(QFont("Microsoft YaHei", 15, QFont.Bold))
        sendSound.setFixedHeight(self.btnSize)
        sendSound.clicked.connect(self.sendSound)

        hl = FlowLayout()
        hl.addWidget(sendTxt)
        hl.addWidget(sendSound)
        hl.setMargin(0)

        vl = QVBoxLayout()
        vl.addWidget(self.textEdit)
        vl.addLayout(hl)
        vl.setMargin(0)
        self.setLayout(vl)

    def sendText(self):
        txt = self.textEdit.toPlainText()
        if len(txt) > 0:
            self.textEntered.emit(txt)
            self.textEdit.clear()

    def sendSound(self):
        record()
        txt = recog().strip(u'，')
        if len(txt) > 0:
            self.textEntered.emit(txt)


class Backend(QThread):
    update = pyqtSignal(str)

    def __init__(self, txt):
        super(Backend, self).__init__()
        self.txt = txt

    def run(self):
        ans = chat(self.txt)
        ans = ans.decode('utf-8')
        self.update.emit(ans)


class PyqtChatApp(QSplitter):
    """聊天界面，QSplitter用于让界面可以鼠标拖动调节"""

    def __init__(self):
        super(PyqtChatApp, self).__init__(Qt.Horizontal)

        self.setWindowTitle('pyChat')  # window标题
        self.setWindowIcon(QIcon('icons/chat.png'))  # ICON
        self.setMinimumSize(800, 600)  # 窗口最小大小

        self.msgList = MsgList()
        # self.msgList.setDisabled(True)  # 刚打开时没有聊天显示内容才对
        self.msgInput = MsgInput()
        self.msgInput.textEntered.connect(self.sendTextMsg)

        rSpliter = QSplitter(Qt.Vertical, self)
        self.msgList.setParent(rSpliter)
        self.msgInput.setParent(rSpliter)

    @pyqtSlot(str)
    def sendTextMsg(self, txt):
        txt = unicode(txt)
        self.msgList.addTextMsg(txt, False, HEAD1)
        self.backend = Backend(txt)
        self.backend.update.connect(self.sendAns)
        self.backend.start()

        # ans = chat(txt)
        # ans = txt
        # self.msgList.addTextMsg(ans, True, HEAD2)

    @pyqtSlot(str)
    def sendAns(self, txt):
        txt = unicode(txt)
        self.msgList.addTextMsg(txt, True, HEAD2)

    def keyPressEvent(self, e):
        if (e.key() == Qt.Key_Escape):
            sys.exit(app.exec_())
        super(PyqtChatApp, self).keyPressEvent(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pchat = PyqtChatApp()
    pchat.show()
    sys.exit(app.exec_())
