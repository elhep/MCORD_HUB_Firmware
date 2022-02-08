#!/usr/bin/python
import socket
import json
import atexit
import time
import csv
from datetime import datetime

HOST, PORT = "10.7.0.220", 5555


class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        res = self.sock.recv(1024)

        print(res.decode('utf-8'))

    def do_cmd(self, obj):
        self.sock.sendall((json.dumps(obj)).encode("utf8"))
        res = self.sock.recv(1024)
        if res:
            res = json.loads(res)
            return res
        else:
            pass

    @staticmethod
    def _csvwriter(filename, *args):
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(args)

    @staticmethod
    def _getTime():
        now = datetime.now()
        return now.strftime("%x"), now.strftime("%H:%M:%S")

    def __del__(self):
        self.sock.sendall((json.dumps(['!disconnect']).encode("utf8")))


cli = Client(HOST, PORT)
atexit.register(cli.__del__)
