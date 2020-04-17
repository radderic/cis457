from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import time
import socket

class ListenThread(QThread):
    listenSignal = pyqtSignal(socket.socket)
    def __init__(self, address, port):
        super(ListenThread, self).__init__()
        self.address = address
        self.port = port
    @pyqtSlot()
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))
        self.socket.listen(1)
        conn, name = self.socket.accept()
        self.listenSignal.emit(conn)

class ReceiveThread(QThread):
    receiveSignal = pyqtSignal(str)
    def __init__(self, conn):
        super(ReceiveThread, self).__init__()
        self.connection = conn
    @pyqtSlot()
    def run(self):
        while(True):
            data = self.connection.recv(1024)
            if not data:
                break
            else:
                self.receiveSignal.emit(data.decode().strip())

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(736, 601)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(40, 90, 641, 401))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setStyleSheet("background: rgb(0, 0, 0)")
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 617, 397))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setObjectName("formLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.SpanningRole, self.verticalLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.sendButton = QtWidgets.QPushButton(self.centralwidget)
        self.sendButton.setGeometry(QtCore.QRect(570, 510, 111, 31))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.pressed.connect(self.send_message)
        self.messageInput = QtWidgets.QLineEdit(self.centralwidget)
        self.messageInput.setGeometry(QtCore.QRect(40, 510, 521, 32))
        self.messageInput.setObjectName("messageInput")
        self.messageInput.returnPressed.connect(self.sendButton.click)
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setGeometry(QtCore.QRect(550, 10, 131, 31))
        self.connectButton.setObjectName("connectButton")
        self.IPInput = QtWidgets.QLineEdit(self.centralwidget)
        self.IPInput.setGeometry(QtCore.QRect(70, 10, 251, 32))
        self.IPInput.setObjectName("IPInput")
        self.portInput = QtWidgets.QLineEdit(self.centralwidget)
        self.portInput.setGeometry(QtCore.QRect(390, 10, 151, 32))
        self.portInput.setObjectName("portInput")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(40, 10, 21, 31))
        self.label_8.setStyleSheet("font: 18pt \"Noto Sans\";")
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(330, 10, 61, 31))
        self.label_9.setStyleSheet("font: 18pt \"Noto Sans\";")
        self.label_9.setObjectName("label_9")
        self.connectionLabel = QtWidgets.QLabel(self.centralwidget)
        self.connectionLabel.setGeometry(QtCore.QRect(40, 60, 381, 21))
        self.connectionLabel.setStyleSheet("font: 18pt \"Noto Sans\";")
        self.connectionLabel.setObjectName("connectionLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 736, 30))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.listenButton = QtWidgets.QPushButton(self.centralwidget)
        self.listenButton.setGeometry(QtCore.QRect(550, 50, 131, 31))
        self.listenButton.setObjectName("listenButton")
        self.listenButton.pressed.connect(self.listen)

        self.connection = None
        self.receiver = None
        self.connectButton.pressed.connect(self.attempt_connect)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.sendButton.setText(_translate("MainWindow", "Send"))
        self.listenButton.setText(_translate("MainWindow", "Listen"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.label_8.setText(_translate("MainWindow", "IP"))
        self.label_9.setText(_translate("MainWindow", "PORT"))
        self.connectionLabel.setText(_translate("MainWindow", "Not Connected"))

    def add_new_message(self, msg):
        msg = msg.strip()
        label = QtWidgets.QLabel(msg)
        label.setStyleSheet("QLabel { color : blue; }");
        self.verticalLayout.addWidget(label)

    def send_message(self):
        msg = self.messageInput.text()
        if(self.connection):
            if(len(msg)):
                self.connection.sendall(msg.encode())
                label = QtWidgets.QLabel(msg)
                label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
                self.verticalLayout.addWidget(label)
                self.messageInput.setText('')

    def attempt_connect(self):
        address = self.IPInput.text()
        port = int(self.portInput.text())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))
        if(sock):
            self.set_connection(sock)

    def set_connection(self, conn):
        self.connection = conn
        self.connectionLabel.setText("Connected with: {}".format(self.connection.getpeername()))
        self.receiver = ReceiveThread(self.connection)
        self.receiver.receiveSignal.connect(self.add_new_message)
        self.receiver.start()

    def listen(self):
        self.listener = ListenThread('127.0.0.1', 5000)
        self.listener.listenSignal.connect(self.set_connection)
        self.connectionLabel.setText("Listening")
        self.listener.start()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
