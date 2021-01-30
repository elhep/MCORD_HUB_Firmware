#!/usr/bin/python
# This script should be started on PC
# Update the hub address below
# It is just a demo of RPC calls
import socket
import sys
import json

HOST, PORT = "172.19.9.116", 1234
data = " ".join(sys.argv[1:])
objects=[
  ["mult",4,5],
  ["mult",7,8],
  ["div",45,0],
  ["div",45,7],
  ]


class client:
  def __init__(self,host,port):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((host,port))
    #Receive the greeting string
    r=""
    self.sockFile = self.sock.makefile()
    c=self.sockFile.readline();
    print(c)
    
  def do_cmd(self,obj):
    self.sock.sendall(json.dumps(obj)+"\n")
    res = self.sockFile.readline()
    res = json.loads(res)
    return res
    
cli=client(HOST,PORT)
for i in objects:
   print cli.do_cmd(i)


