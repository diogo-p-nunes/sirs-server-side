from encryptor import *
import subprocess
from constants import *
import os


def getFileByteArray(filename):
    with open(filename, 'r') as f:
        output = f.read()
    return bytearray(output, 'utf-8')

def writeToFile(filename, data, type):
    with open(filename, type) as f:
        f.write(data)

def openFile(filename):
    command = "cat " + filename
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)

def readFile(filename):
    with open(filename, "r") as f:
        output = f.readlines()
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


def getFileName(key,filelist):
    return os.getcwd() + "/" + FILE_SYSTEM + filelist[key]



