import network
import _thread
import usocket
import ujson
import misc
import afedrv


BUFFER_SIZE = 1024
DISCONNECTED_MESSAGE = '!disconnect'
# Functions which process requests
def test_proper_connection():
    if serv:
        return ('OK','Connected')
    else:
        return ('ERR','Not Connected')
    
def loop_for_list_arg(func,obj):
    result = dict()
    for board in obj:
        try:
            result[board] = func(board)
        except:
            result[board] = 'ERR'
    return ('OK', result)

def loop_for_afe_list_arg(func,obj1,obj2,obj3):
    result = dict()
    for num,v1,v2 in zip(obj1,obj2,obj3):
        try:
            result[num] = func(num,v1,v2)
        except:
            result[num] = 'ERR'
    return ('OK', result)
   

def initialization(obj):
    if isinstance(obj[1], list):
        return loop_for_list_arg(misc.init,obj[1])
    else:
        return ('OK', misc.init(obj[1]))

def turn_on(obj):
    if isinstance(obj[1], list):
        return loop_for_list_arg(misc.HVon,obj[1])
    return('OK', misc.HVon(obj[1]))

def turn_off(obj):
    if isinstance(obj[1], list):
        return loop_for_list_arg(misc.HVoff,obj[1])
    return ('OK', misc.HVoff(obj[1]))

def setdac(obj):
    if isinstance(obj[1], list):
        return loop_for_afe_list_arg(afedrv.SetDac,obj[1],obj[2],obj[3])
    return ('OK', afedrv.SetDac(obj[1],obj[2],obj[3]))

def getsimpiterlopp():
    pass

def getadc(obj):
    return('OK',afedrv.GetAdc(obj[1],obj[2]))

# Table of functions
func = {
    'init': initialization,
    'hvon': turn_on,
    'hvoff': turn_off,
    'setdac':setdac,
    'test':test_proper_connection,
    'getsimploop': getsimpiterlopp,
    'adc':getadc
}


class Ctlsrv():
    def __init__(self):
        # Start Ethernet
        self.lan = network.LAN()
        self.lan.active(1)
        # Start server
        self.srvthread = None
        self.runflag = False
        self.ip = None
    
    def getip(self):
        self.ip = self.lan.ifconfig()[0]

    def __str__(self):
        self.getip()
        return 'AFE HUB %s' % (self.ip)
    
    @staticmethod
    def send_msg(cl, msg):
        cl.sendall((ujson.dumps(msg)).encode("utf8"))
        
    def get_IP(self):
        print(self.lan.ifconfig())

    def srv_handle(self, port):
        addr = usocket.getaddrinfo('0.0.0.0', port)[0][-1]
        print(addr)
        s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        s.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        s.bind(addr)
        print(s)
        s.listen(1)
        print('listening on', addr)
        while self.runflag:
            cl,addr = s.accept()
            print('client connected from', addr)
            Ctlsrv.send_msg(cl, ('Client connected with %s' % (self)))
            while True:
                try:
                    json = cl.recv(BUFFER_SIZE)
                except Exception as e:
                    res = ('ERR', str(e))
                    break
                
                try:
                    cmd = ujson.loads(json)
                    print(cmd[0])
                    if cmd[0] == DISCONNECTED_MESSAGE: break
                    res = func[cmd[0]](cmd)
                except Exception as e:
                    res = ('ERR', str(e))
                Ctlsrv.send_msg(cl, res)

            cl.close()
            
            

    def run(self, port):
        if self.srvthread:
            raise(Exception("Server already running"))
        self.runflag = True
        self.srvthread = _thread.start_new_thread(self.srv_handle, (port,))
        return

    def stop(self):
        self.runflag = False

        return


serv = Ctlsrv()
serv.run(5555)

