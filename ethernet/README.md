# Implementation of TCP/IP control server in AFE hub

AFE hub works under control of MicroPython interpreter. It may be accessed via USB interface, working as a serial console, but such solution is inconvenient, if we need to control multiple hubs.
MicroPython offers a possibility to access the interpreter's command line via network, so called *webrepl* , but this solution is not suitable for control.

The desired solution must enable remote execution of procedures implemented in MicroPython, and reliable transfer of arguments and results via TCP/IP network.
Such a solution for normal Python, based on msgpack library was developed and realeased to Public Domain by Wojciech M. Zabolotny in 2012 in post [Simple object based RPC for Python](http://ftp.funet.fi/pub/archive/alt.sources/2722.gz) on alt.sources Usenet group.
Unfortunately, this solution can't be directly used in the AFE hub, because of too big size of necessary libraries.
The *umsgpack* library occupies ca. 38 KB, while the necessary *datetime* library occupies ca. 73 KB, which fully fills the on-chip FLASH in STM32767 microcontroller used in the hub. Of course the problem may be worked
around by using the additional SD card, but that makes system fully dependent on  installation of the SD card.

The msgpack-based encapsulation may be replaced by JSON. Of course it increases the network traffic, 
but for control of AFE hub it is acceptable. In standard mode the MicroPython JSON module serializes objects
as single text line with EOL at the end. That simplifies separation of objects from the TCP/IP data stream.

The resulting solution uses very simple network protocol:

* The RPC function call is delivered to the server as a single-line serialized JSON list. 
  The first element of the list is a string containing the name of the function to be called in the server.
  Next elements of the list are function arguments. The whole list (including the name) is passed to the function.
  That allows efficient implementation of functions with behavior depending on the name, by which the function is called.
* The results of the function is also returned as a the list, where the first element is the status ("ERR" or "OK"), and the following elements are the results (depending on the function).

Due to limited RAM memory capacity, the server is sensitive to sending too long requests. Therefore the user may the maximum size of the request in the constant `CMD_LIMIT`. If the client tries to send a request longer than the limit, the error is reported and the connection is closed.

The user should define the dictionary mapping the names of the functions to the real Python functions.
Following is an example of very simple functions with the corresponding dictionary:

    CMD_LIMIT=30
    #Functions which process requests
    def remote_mult(obj):
      return ('OK', obj[1]*obj[2])
      
    def sum_vals(obj):
      res = 0
      for v in obj[1:]:
          res += v
      return ('OK', res)

    def remote_div(obj):
      if obj[2] == 0:
          return ('ERR','I can not divide by 0')
      return ('OK', obj[1]/obj[2])

    #Table of functions
    func={
       'mult':remote_mult,
       'sum':sum_vals,
       'div': remote_div,
      }


The current solution handles only one client at a time and handles only one request at a time. Hence, it eliminates need for locking. In case if the simultaneous access via serial console should be possible, or data may be accessed from other threads, it is the user's responsibility to provide the appropriate locking.

It is important, that the `_thread` module is enabled in the MicroPython.
The developer must ensure that the following settings are present in the `mpconfigboard.h` file in the appropriate board definition.

        #define MICROPY_PY_THREAD           (1)
        #define MICROPY_PY_THREAD_GIL       (1)

The server should be started with the following commands (assuming that it should listen on the 134 port).


       import ctrl_server as cs
       [...]
       s1=cs.ctlsrv()
       s1.run(1234)


The minimalistic client connecting to the server is shown below:

    #!/usr/bin/python
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

