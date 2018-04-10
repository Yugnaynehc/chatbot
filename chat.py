from PySide.QtCore import *
from PySide.QtGui import *
import sys
import chatUi
import socket
import threading
import socket
import select
import string
from Seq2Seq import chat


class ChatMain(QWidget, chatUi.Ui_Form):
    def __init__(self, parent=None):
        super(ChatMain, self).__init__(parent)
        self.setupUi(self)
        self.text = ''
        self.connect(self.sendButton, SIGNAL('clicked()'), self.send)

    pressed = Signal(str)

    def send(self):
        ques = self.msgEdit.text()
        # self.pressed.emit(ques+'\n')
        self.say_punched('You: '+ques+'\n')
        self.msgEdit.setText('')
        ans = chat(ques)
        self.say_punched('Bot: '+ans+'\n')

    Slot(str)

    def say_punched(self, data):
        self.text += data
        self.chatEdit.setText(self.text)


app = QApplication(sys.argv)
form = ChatMain()
form.show()
app.exec_()
