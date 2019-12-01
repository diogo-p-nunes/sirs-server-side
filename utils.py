import subprocess
import os
from constants import *
import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


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


# intermediate version
def addTimestamp(m):
    print("+ timestamp")
    timestamp = str(datetime.datetime.utcnow())
    #if isinstance(m, (bytes, bytearray)):
    #    #m = m + b'||' + timestamp.encode()
    #    m = m
    #else:
    #    m = m + TSMP + timestamp
    return m + TSMP + timestamp.encode()


def addSignature(m):
    print("+ signature")
    return m + SIGN + messageSignature(m)


def convertToBytes(m):
    if isinstance(m, (bytes, bytearray)):
        return m
    else:
        return m.encode()


# intermediate version
def messageSignature(m):
    priv = RSA.import_key(open("private_key.pem").read())
    h = SHA256.new(m)
    return pkcs1_15.new(priv).sign(h)
