# misc.py
import time
import pyb
import afedrv
import hub

def HVon(id):
	pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
	pyb.Pin.cpu.E12.value(1)
	afedrv.SetAllHV(id)

def HVoff(id):
	pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
	pyb.Pin.cpu.E12.value(0)
	afedrv.ClrAllHV(id)

def testSipmOn(id):
	HVon(id)
	afedrv.SetDac(id, 60, 60)

def testSipmOff(id):
	HVoff(id)