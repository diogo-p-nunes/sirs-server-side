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


def checkDeviceConnected(btManager):
    if not btManager.hasConnectedDevices():
        print("[MENU] No device connected :(")
        return False
    else:
        return True

def getEncryptableFiles(btManager):
    lista = [file for file in sorted(os.listdir(FILE_SYSTEM)) if not file.startswith("metadata")]
    for line in readFile(LINKEDFILES):  
        parts = line.split("|")
        partfile = (parts[1].split("/"))[-1]
        if partfile in lista: # and parts[0] != btManager.active_device.addr: 
            #assim SÓ faz remove de files que ja estejam encryptados:
            # por outras pessoas ou com outras pessoas > ou seja pode fazer share de ficheiros encryptados apenas por ele
            lista.remove(partfile)

    return lista


def getOpenableFiles(btManager):
    allfiles = [file for file in sorted(os.listdir(FILE_SYSTEM)) if not file.startswith("metadata")]
    device = btManager.active_device
    linkedfiles = readFile(LINKEDFILES)
    openable = []
    for f in allfiles:
        if f not in [f.split("|")[1].split("/")[-1] for f in linkedfiles]:
            openable.append(f)
    
    for lf in linkedfiles:
        if device.addr == lf.split("|")[0]:
            f = lf.split("|")[1].split("/")[-1]
            if f not in openable: openable.append(f)

    '''
    #filestoremove = []
    filesnottoremove = []
    for line in readFile(LINKEDFILES):
        parts = line.split("|")
        if parts[0] != device.addr: 
            #lista.remove((parts[1].split("/"))[-1])
            filestoremove.append((parts[1].split("/"))[-1])
        if parts[0] == device.addr:
            filesnottoremove.append((parts[1].split("/"))[-1])
    #check if any of the files to remove is a shared file 
    # because she has the right to open her share files  
    for rem in filestoremove:
        if rem not in filesnottoremove:
            lista.remove(rem)
    '''

    
    return sorted(openable)


def convertToBytes(m):
    if isinstance(m, (bytes, bytearray)):
        return m
    else:
        return m.encode()


def splitMessage(m, isPUK=False, isMetadata=False):
    if isMetadata:
        #print("isMetadata")
        #print(m)
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

