#!/usr/bin/env python3
import os
import socket
import signal
from sys import exit
from threading import Thread

class Server:
    def __init__(self, address='127.0.0.1', port=5000):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        signal.signal(signal.SIGINT, self.__sig_handler)
        self.commands = {
            'list': self.__list,
            'retrieve': self.__retrieve,
            'store': self.__store,
        }

    def __sig_handler(self, signum, frame):
        #try to somewhat gracefully end the process
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        exit(1)

    def __send(self, conn, data):
        conn.sendall(data.encode('utf-8'))

    def __list(self, conn, args):
        cur_dir = os.listdir('.')
        dir_str = "\n".join(cur_dir)+"\n"
        self.__send(conn, dir_str)

    def __retrieve(self, conn, args):
        filename = args[0]
        size = 0
        data = None
        if os.path.isfile(filename):
            f = open(filename, 'rb')
            data = f.read()
            size = len(data)
            self.__send(conn, str(size))
            conn.sendall(data)
        else:
            self.__send(conn, str(size))

    def __store(self, conn, args):
        filename = args[0]
        size = int(args[1])
        f = open(filename, 'wb')
        bytes_recv = 0
        while(bytes_recv < size):
            data = conn.recv(1024)
            bytes_recv += len(data)
            f.write(data)
        f.close()

    def __end_connection(self, conn):
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def __parse_data(self, data):
        data = data.decode().split(' ', 1)
        if len(data) == 2:
            return data[0], data[1].split(' ')
        else:
            return data[0], None

    def __client_connection(self, conn, name):
        while(True):
            data = conn.recv(64)
            if not data:
                print('Closing connection with {}'.format(conn.getpeername()))
                break
            else:
                command, args = self.__parse_data(data)
                if command in self.commands:
                    self.commands[command](conn, args)
        self.__end_connection(conn)

    def listen(self):
        self.socket.listen(4)
        while(True):
            conn, name = self.socket.accept()
            print("Connection from {}".format(name))
            t = Thread(target=self.__client_connection, args=(conn,name))
            t.start()

s = Server()
s.listen()
