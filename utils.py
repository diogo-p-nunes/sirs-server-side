import subprocess
import os
from constants import *


def writeToFile(filename, data, mode):
    with open(filename, mode) as f:
        f.write(data)


def readFile(filename, mode="r"):
    with open(filename, mode) as f:
        if mode != "rb":
            output = f.readlines()
        elif mode == "rb":
            output = f.read()
    return output


def connectDevice(btManager):
    device = btManager.connect()
    if device is not None:
        if not btManager.isDeviceRegistered(device):
            print("[MENU] Device is NOT registered, sending NOK")
            btManager.registerDevice(device)
        print("[MENU] Device is registered and connected.")
    else:
        print("[MENU] Device NOT connected.")


def getFileName(key, filelist):
    return os.getcwd() + "/" + FILE_SYSTEM + filelist[key]


def getEncryptableFiles(btManager):
    if not btManager.hasConnectedDevices():
        print("[MENU] No device connected :(")
        return None
    lista = [file for file in sorted(os.listdir(FILE_SYSTEM)) if not file.startswith("metadata")]
    device = btManager.getDevice()
    for line in readFile(LINKEDFILES):
        parts = line.split("|")
        if parts[0] != device.addr or parts[2].startswith("E"):
            lista.remove((parts[1].split("/"))[-1])
    return lista


def getOpenableFiles(btManager):
    if not btManager.hasConnectedDevices():
        print("[MENU] No device connected :(")
        return None
    lista = [file for file in sorted(os.listdir(FILE_SYSTEM)) if not file.startswith("metadata")]
    device = btManager.getDevice()
    for line in readFile(LINKEDFILES):
        parts = line.split("|")
        if parts[0] != device.addr:
            lista.remove((parts[1].split("/"))[-1])
    return lista



