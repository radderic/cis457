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
        self.max_backlog = 2
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))
        signal.signal(signal.SIGINT, self.__sig_handler)
        self.count = 0
        self.run_threads = True
        self.commands = {
            'list': self.__list,
            'retrieve': self.__retrieve,
            'store': self.__store,
        }

    def __sig_handler(self, signum, frame):
        #try to somewhat gracefully end the process to avoid OS bind issues
        self.run_threads = False
        print("Waiting for threads to finish")
        while(self.count > 0):
            pass
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        exit(1)

    def __send(self, conn, data):
        conn.sendall(data.encode('utf-8'))

    def __list(self, conn, args):
        print("A list request by {}".format(conn.getpeername()))
        cur_dir = os.listdir('.')
        dir_str = "\n".join(cur_dir)+"\n"
        self.__send(conn, dir_str)

    def __retrieve(self, conn, args):
        filename = args[0]
        print("A retrieve request by {} for file {}".format(conn.getpeername(), filename))
        size = 0
        data = None
        if os.path.isfile(filename):
            f = open(filename, 'rb')
            data = f.read()
            size = len(data)
            self.__send(conn, str(size))
            response = conn.recv(16).decode()
            if(response == 'ready'):
                conn.sendall(data)
        else:
            self.__send(conn, str(size))

    def __store(self, conn, args):
        filename = args[0]
        size = int(args[1])
        print("A store request by {} for file {} ({} bytes)".format(conn.getpeername(), filename, size))
        f = open(filename, 'wb')
        bytes_recv = 0
        while(bytes_recv < size):
            data = conn.recv(1024)
            bytes_recv += len(data)
            f.write(data)
        f.close()

    def __end_connection(self, conn):
        print("ending connection with {}".format(conn.getpeername()))
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def __parse_data(self, data):
        data = data.decode().split(' ', 1)
        if len(data) == 2:
            return data[0], data[1].split(' ')
        else:
            return data[0], None

    def __client_connection(self, conn, name):
        conn.settimeout(2)
        data = None
        while(self.run_threads):
            try:
                data = conn.recv(64)
            except socket.timeout:
                continue
            if not data:
                print('Closing connection with {}'.format(conn.getpeername()))
                break
            else:
                command, args = self.__parse_data(data)
                if command in self.commands:
                    self.commands[command](conn, args)
        self.count -= 1
        print("Connections: {}".format(self.count))
        self.__end_connection(conn)

    def listen(self):
        print("Server running as: {}".format(self.socket.getsockname()))
        self.socket.listen(self.max_backlog)
        while(True):
            conn, name = self.socket.accept()
            self.count += 1
            print("Connection from {}".format(name))
            print("Connections: {}".format(self.count))
            t = Thread(target=self.__client_connection, args=(conn,name))
            t.start()


if __name__ == "__main__":
    s = Server()
    s.listen()
