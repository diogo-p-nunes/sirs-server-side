import hashlib
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
        # remove every file that is not public
        parts = line.split("|")
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


def convertToBytes(m):
    if isinstance(m, (bytes, bytearray)):
        return m
    else:
        return m.encode()


def splitMessage(m, isPUK=False, isMetadata=False):
    if isMetadata:
        #print("isMetadata")
        bcontent = m[:53]
        btimestamp = m[56:75]
        bsignature = m[78:]
    elif isPUK:
        #print("isPUK")
        bcontent = m[:450]
        btimestamp = m[453:472]
        bsignature = m[475:]
    else:
        #print("isNormal")
        bcontent = m[:2]
        btimestamp = m[5:24]
        bsignature = m[27:]
    #print(bcontent)
    #print(btimestamp)
    #print(bsignature)
    return (bcontent, btimestamp, bsignature)

