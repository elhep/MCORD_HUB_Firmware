from array import array
import time
import pyb


class HUB:

    def __init__(self) -> None:
        self.can = pyb.CAN(1)
        self.can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,sjw=1, bs1=7, bs2=2, auto_restart=True)
        self.can.setfilter(0, self.can.MASK16, 0, (0, 0, 0, 0))
        self.pin_volage = pyb.Pin.cpu.E12
         
    @staticmethod
    def _set_buff_with_values(size,*values):
        buff = bytearray(size)
        for i,val in zip(len(buff),values):
            buff[i] = val
        return buff

    @staticmethod
    def _set_clean_buff(size):
        return bytearray(size), [0, 0, 0, memoryview(bytearray(size))]
    
    @staticmethod
    def _convert_from_volt_to_dac(*values):
        return [(-271.2)*val+ 18142 for val in values]

    #translate old method to OOP(trial)
    def GetVer(self,id):
        """
        This function helps to checkout version of AFE on direct ID.
        [ARGUMENTS]: id:int 

        """
        self.can.send("\x00\x01",id)
        _ , lst = self._set_clean_buff(8)
        self.can.recv(0,lst)

        print("ID: ", lst[0])
        print("RTR: ", lst[1])
        print("FMI: ", lst[2])
        VerH = (lst[3][2] << 8) | (lst[3][3] & 0xff)
        print("VerH: ", VerH)
        VerL = (lst[3][4] << 8) | (lst[3][5] & 0xff)
        print("VerL: ", VerL)
        VerD = (lst[3][6] << 8) | (lst[3][7] & 0xff)
        print("VerD: ", VerD)

        return VerH,VerD,VerL

    def GetAdc(self,id, chn):
        """
        This function helps to get out information about current characteristic of 
        using SiPM.
        [ARGUMENTS]: id:int, chn:int
        [CHN]: 1-2: offset, 3-4: voltage, 5-6: current 
        
        """
        if chn >= 1 and chn <= 3: self.can.send("\x00\x10", id)
        elif chn >= 4 and chn <= 6: self.can.send("\x00\x11", id)
        else: return 
     
        time.sleep(1)
        _, lst = self._set_clean_buff(8)
        self.can.recv(0, lst)

        print("ID: ", lst[0])
        print("RTR: ", lst[1])
        print("FMI: ", lst[2])
        if chn == 1:
            AdcValue = (lst[3][2] << 8) | (lst[3][3] & 0xff)
            print("adc value of ch", chn, ":", AdcValue, "V")
        elif chn == 2:
            AdcValue = (lst[3][4] << 8) | (lst[3][5] & 0xff)
            print("adc value of ch", chn, ":", AdcValue, "V")
        elif chn == 3:
            AdcValue = (lst[3][6] << 8) | (lst[3][7] & 0xff)
            #AdcValue = AdcValue * (70/4095)
            print("adc value of ch", chn, ":", AdcValue)
        elif chn == 4:
            AdcValue = (lst[3][2] << 8) | (lst[3][3] & 0xff)
            #AdcValue = AdcValue * (70/4095)
            print("adc value of ch", chn, ":", AdcValue)
        elif chn == 5:
            AdcValue = (lst[3][4] << 8) | (lst[3][5] & 0xff)
            print("raw adc value of ch", chn, ":", AdcValue, "I")
            print("adc value of ch [uA]", chn, ":", AdcValue, "I")
        elif chn == 6:
            AdcValue = (lst[3][6] << 8) | (lst[3][7] & 0xff)
            print("adc value of ch", chn, ":", AdcValue, "I")

        return AdcValue

    def SetDac(self, id, val1, val2):
        """
        This function helps to set up voltage on 2 SiPM per board.
        [ARGUMENTS]: id:int, val1:float, val2:float
        [valx]: value of voltage on master and slave simp.  
        
        """
        val1conv,val2conv = self._convert_from_volt_to_dac(val1,val2)
        print("dac1: ", int(val1conv), "dac2: ", int(val2conv))
        buf = self._set_buff_with_values(6,0x00,0x12,(int(val1conv) >> 8) & 0xFF,int(val1conv) & 0xFF,
                                        (int(val2conv) >> 8) & 0xFF,int(val2conv) & 0xFF)
        self.can.send(buf, id)
        time.sleep(1)
        print(self.can.recv(0))
        return (int(val1conv), int(val2conv))

    
    def GetTemp(self,id):
        """
        This function helps to get information about temerature from board
        [ARGUMENTS]: id:int
        """
        self.can.send("\x00\x13", id)
        time.sleep(1)
       
        _, lst = self._set_clean_buff(6)
        self.can.recv(0, lst)
        print("ID: ", lst[0])
        print("RTR: ", lst[1])
        print("FMI: ", lst[2])
        TempVal1 = (lst[3][2] << 8) | (lst[3][3] & 0xff)
        print("temp value 1: ", TempVal1, "bits")
        TempVal2 = (lst[3][4] << 8) | (lst[3][5] & 0xff)
        print("temp value 2: ", TempVal2, "bits")
        return(TempVal1,TempVal2)


    def SetDigRes(self,id, chn, val):
        """
        This function helps to set up offset to current SiPM 
        [ARGUMENTS]: id:int, chn:int, val:int 
        [CHN]: 0 - master SiPM, 1 - slave SiPM
        [VAL]: 0 - 255
        """
        buf = self._set_buff_with_values(4,0x00,0xA0,((chn) & 0xFF),((val) & 0xFF))
        self.can.send(buf, id)
        time.sleep(1)
        print(self.can.recv(0))
        
    def SetAllHV(self,id):
        """
        This function turn on SiPM on AFE Lvl
        [ARGUMENTS]: id:int
        """
        buf = self._set_buff_with_values(6,0x00,0x40,0,0,0,3)
        self.can.send(buf, id)
        time.sleep(1)
        print(self.can.recv(0))
        
    def ClrAllHV(self,id):  
        """
        This function turn on SiPM on AFE Lvl
        [ARGUMENTS]: id:int
        """
        buf = self._set_buff_with_values(6,0x00,0x41,0,0,0,3)
        self.can.send(buf, id)
        time.sleep(1)
        print(self.can.recv(0))
        
    ############################################################## -> Methods to control procedures 
    #get better way to 1 turn on and turn off, maybe some methods to procedure should be in other class
    def HVon_boot(self,id):
        """
        Methos used to turn on procedure with Pin up 
        [ARGUMENTS]: id:int
        """
        self.pin_volage.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
        self.pin_volage.value(1)
        self.SetAllHV(id)
        
        
    def HVon(self,id):
        """
        Methos used to turn on procedure
        [ARGUMENTS]: id:int
        """
        self.SetAllHV(id)
        
    def HVoff_boot(self,id):
        """
        Methos used to turn off procedure with Pin down 
        [ARGUMENTS]: id:int
        """
        self.pin_volage.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
        self.pin_volage.value(0)
        self.ClrAllHV(id)
    
    def HVon(self,id):
        """
        Methos used to turn off procedure
        [ARGUMENTS]: id:int
        """
        self.ClrAllHV(id)
        
    def init(self,id):
        """
        Methos used to initialization SiPM with proper offset and start voltage values
        [ARGUMENTS]: id:int
        """
        self.SetDac(id, 53, 53)
        self.SetDigRes(id, 0, 200)
        self.SetDigRes(id, 1, 200)
     
        
    
    
        

     








