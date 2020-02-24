#!/usr/bin/env python3
import socket
import errno
import os
import sys

class Client:
    def __init__(self, address='127.0.0.1', port=5000):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commands = {
            'connect': {
                'func': self.connect,
                'argc': 2
            },
            'list': {
                'func': self.list,
                'argc': 0
            },
            'retrieve': {
                'func': self.retrieve,
                'argc': 1
            },
            'store': {
                'func': self.store,
                'argc': 1
            },
            'quit': {
                'func': self.quit,
                'argc': 0
            },
            'help': {
                'func': self.help,
                'argc': 0
            },
            'exit': {
                'func': self.exit,
                'argc': 0
            }

        }

    def __parse_input(self, user_input):
        data = user_input.split(' ', 1)
        if len(data) == 2:
            return data[0], data[1]
        else:
            return data[0], None

    def connect(self, args):
        '''
        > connect [ip address] [port]
        Connects to a ftp server:
        '''
        self.address = args[0]
        if args[1].isdigit():
            self.port = int(args[1])
        else:
            print("Invalid port:", args[1])
            return
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except socket.error as error:
            pass
        #create a new socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.address, self.port))
        except socket.error as error:
            print("Failed to connect:", os.strerror(error.errno))

    def list(self, args):
        '''
        > list
        Requests a list of files on the server.
        '''
        self.__send("list")
        try:
            data = self.socket.recv(1024)
            print(data.decode())
        except socket.error as error:
            print("Failed to recv:", os.strerror(error.errno))

    def retrieve(self, args):
        '''
        > retrieve [file name]
        Requests a file from the server. Saves to current directory.
        '''
        filename = args[0]
        self.__send("retrieve {f}".format(f=filename))
        file_size = int(self.socket.recv(32))
        if(file_size == 0):
            print("File does not exist")
            return
        self.__send("ready")
        bytes_recv = 0
        f = open(filename, 'wb')
        print("file size:", file_size)
        while(bytes_recv < file_size):
            data = self.socket.recv(1024)
            bytes_recv += len(data)
            f.write(data)
        f.close()
        print("Wrote {s} bytes to {f}".format(s=file_size, f=filename))

    def store(self, args):
        '''
        > store [file name]
        Copies a file to the server.
        '''
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
        '''
        > quit
        Closes the connection to the server
        '''
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
            print('Connection ended')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as error:
            print("Failed to quit:", os.strerror(error.errno))

    def help(self, args):
        '''
        > help
        Lists commands description and usage.
        '''
        for k,v in self.commands.items():
            print(v['func'].__doc__)

    def exit(self, args):
        '''
        > exit
        Exits the current program.
        '''
        sys.exit(0)

    def __send(self, data):
        try:
            self.socket.sendall(data.encode('utf-8'))
        except socket.error as error:
            print("Failed to send:", os.strerror(error.errno))

    def __validate(self, command, raw_args):
        if command not in self.commands:
            print("Invalid command:", command)
            return False, None
        argc = 0
        args = None
        if not raw_args:
            argc = 0
        else:
            args = raw_args.split(' ')
            argc = len(args)
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

            command, args = self.__parse_input(user_input)
            is_valid, args = self.__validate(command, args)
            if is_valid:
                self.commands[command]['func'](args)
            elif not user_input:
                pass

c = Client()
c.run()
