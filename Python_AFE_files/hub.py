# hub.py
import time
import pyb

def SetHV():
	pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
	pyb.Pin.cpu.E12.value(1)

def ClrHV():
	pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
	pyb.Pin.cpu.E12.value(0)