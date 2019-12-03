from utils import writeToFile, readFile, convertToBytes
from encryptor import addTimestamp, addSignature
from constants import *
import os


class Device:
    def __init__(self, socket, addr, puk_filename=None):
        self.socket = socket
        self.addr = addr
        self.puk_filename = puk_filename
        self.doneConfAssurance = False

    def setPukFilename(self, puk_filename):
        self.puk_filename = puk_filename

    def getPukFilename(self):
        if self.puk_filename is not None:
            return self.puk_filename
        else:
            # ask data from android
            print("[DEVICE] Requesting PUK to Android")
            try:
                data = self.socket.recv(1076)
                if len(data) == 0:
                    return None
            except IOError:
                print("[DEVICE] Error: Puk not received")
                return None
            name = PUKDIR + "/" + self.addr.replace(':', '') + ".pem"
            writeToFile(name, data, 'wb')
            self.setPukFilename(name)
            return self.getPukFilename()

    def readMessage(self, size):
        try:
            data = self.socket.recv(size)
            if len(data) == 0:
                return None
            return data
        except IOError:
            print("[DEVICE] Error: Message not received")
            return None

    def isConnected(self):
        try:
            self.socket.getpeername()
            return True
        except:
            self.socket = None
            return False

    def setDoneConfAssurance(self, value):
        self.doneConfAssurance = value

    def getRegistrationEntry(self):
        return self.addr + "|" + self.getPukFilename()

    def sendMessage(self, m):
        m = convertToBytes(m)
        original = m
        m = addTimestamp(m)
        #m = addSignature(m,original)
        self.socket.send(m)

    def requestMetadataContent(self, filename):
        print("[DEVICE] Requesting metadata content")
        self.sendMessage("REQ_DESENCRYPT")
        answer = self.readMessage(2).decode("utf-8")
        metafile = FILE_SYSTEM + "metadata." + filename.split("/")[-1]
        if answer == "OK":
            size = os.path.getsize(metafile)
            print("[DEVICE] Sending metadata size")
            self.sendMessage(str(size))
            print("[DEVICE] Sending metadata")
            self.sendMessage(readFile(metafile, "rb"))
            content = self.readMessage(120)
            print("[DEVICE] Got metadata content")
            print("[DEVICE] Metadata content received:", content)
            # returns list = [symmetric-key, digest, nonce]
            return content.split(CNT)
        else:
            print("[DEVICE] Error: Decryption key not received")
            return None
