import misc
from new_afedrv import HUB
from server import Ctlsrv

#init HUB functions
hub = HUB()

#init Server 
serv = Ctlsrv()
serv.run(5555)