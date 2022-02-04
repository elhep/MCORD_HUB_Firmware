# misc.py
import time
import pyb
import afedrv
import hub
import os


def HVon(id):
    pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
    pyb.Pin.cpu.E12.value(1)
    afedrv.SetAllHV(id)


def HVoff(id):
    pyb.Pin.cpu.E12.init(pyb.Pin.OUT_PP, pyb.Pin.PULL_NONE)
    pyb.Pin.cpu.E12.value(0)
    afedrv.ClrAllHV(id)


def init(id):
    x = afedrv.SetDac(id, 53, 53)
    afedrv.SetDigRes(id, 0, 200)
    afedrv.SetDigRes(id, 1, 200)
    return x

