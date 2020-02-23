#!/usr/bin/env python3
import socket
import errno
import os

class Client:
    def __init__(self, address='127.0.0.1', port=5000):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commands = {
            'connect': {
                'func': self.connect,
                'argc': 2 },
            'list': {
                'func': self.list,
                'argc': 0 },
            'retrieve': {
                'func': self.retrieve,
                'argc': 1 },
            'store': {
                'func': self.store,
                'argc': 1 },
            'quit': {
                'func': self.quit,
                'argc': 0 }
        }

    def __parse_input(self, user_input):
        data = user_input.split(' ', 1)
        if len(data) == 2:
            return data[0], data[1]
        else:
            return data[0], None

    def connect(self, args):
        self.address = args[0]
        if args[1].isdigit():
            port = int(args[1])
        else:
            print("Invalid port:", args[1])
            return
        try:
            self.socket.connect((self.address, self.port))
        except socket.error as error:
            print("Failed to connect:", os.strerror(error.errno))

    def list(self, args):
        self.__send("list")
        data = self.socket.recv(1024)
        print(data.decode())

    def retrieve(self, args):
        filename = args[0]
        self.__send("retrieve {f}".format(f=filename))
        file_size = int(self.socket.recv(32))
        if(file_size == 0):
            print("File does not exist")
            return
        bytes_recv = 0
        f = open(filename, 'wb')
        print("file size:", file_size)
        while(bytes_recv < file_size):
            data = self.socket.recv(1024)
            bytes_recv += len(data)
            print("got:", bytes_recv)
            f.write(data)
        f.close()
        print("Wrote to {s} to {f}".format(s=file_size, f=filename))

    def store(self, args):
        filename = args[0]
        if not os.path.isfile(filename):
            print("File does not exist")
            return
        size = os.path.getsize(filename)
        data = "store {name} {size}".format(name=filename, size=size)
        self.__send(data)
        f = open(filename, 'rb')
        self.socket.sendall(f.read())
        f.close()

    def quit(self, args):
        print('Connection ended')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __send(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def __validate(self, command, raw_args):
        print("command: {} args: {}".format(command, raw_args))
        #invalid command
        if command not in self.commands:
            print("{} not in commands".format(command))
            return False, None
        #valid command but no args
        if not raw_args:
            print("No args, but valid command")
            return True, None
        #valid command with args
        args = raw_args.split(' ')
        argc = len(args)
        #valid command with insufficient args
        if argc < self.commands[command]['argc']:
            print("Valid command but insufficient args")
            return False, None
        return True, args

    def run(self):
        user_input = ''
        while(True):
            try:
                user_input = input("> ").lower()
            except EOFError:
                return

            if user_input == 'exit':
                return

            command, args = self.__parse_input(user_input)
            #if command in self.commands:
            is_valid, args = self.__validate(command, args)
            if is_valid:
                self.commands[command]['func'](args)
            else:
                print("Invalid command:", command)

c = Client()
c.run()
