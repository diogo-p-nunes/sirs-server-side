from encryptor import *
import subprocess
from constants import *
import os


def getFileByteArray(filename):
    with open(filename, 'r') as f:
        output = f.read()
    return bytearray(output, 'utf-8')


def openFile(filename):
    command = "cat " + filename
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)


def connectDevice(btManager):
    device = btManager.connect()
    if device is not None:
        if not btManager.isDeviceRegistered(device):
            btManager.registerDevice(device)
        print("Device is registered and connected.")
    else:
        print("Device NOT connected.")


def getFileName(key):
    return os.getcwd() + "/" + FILE_SYSTEM + os.listdir(FILE_SYSTEM)[key]



