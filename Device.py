from utils import *
from encryptor import *
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
            data = self.readMessage(731, isPUK=True)
            name = PUKDIR + "/" + self.addr.replace(':', '') + ".pem"
            writeToFile(name, data, 'wb')
            self.setPukFilename(name)
            return self.getPukFilename()

    def readMessage(self, size, isPUK=False, isMetadata=False):
        try:
            data = self.socket.recv(size)
            if len(data) == 0:
                return None
            #print(len(data))
            bcontent, btimestamp, bsignature = splitMessage(data, isPUK=isPUK, 
                                                                  isMetadata=isMetadata)
            success_ts = verifyTimeStamp(btimestamp)
            if not success_ts:
                print("[DEVICE] Error: Timestamp is invalid.")
                return None
            print("[DEVICE] Timestamp is valid.")
            
            if not isPUK:
                success_sign = verifySignature(bcontent+TSMP+btimestamp, 
                                                bsignature, 
                                                self.getPukFilename())
            else:
                success_sign = True

            if not success_sign:
                print("[DEVICE] Error: Signature is invalid.")
                return None
            print("[DEVICE] Signature is valid.")

            return bcontent
        except IOError:
            print("[DEVICE] Error: Message not received.")
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
        m = addTimestamp(m)
        m = addSignature(m)
        self.socket.send(m)

    def requestMetadataContent(self, filename):
        print("[DEVICE] Requesting metadata content")
        self.sendMessage("RE")
        answer = self.readMessage(285).decode("utf-8")
        metafile = FILE_SYSTEM + "metadata-" + (self.addr).replace(":","-")+ "." + filename.split("/")[-1]
        if answer == "OK":
            print("[DEVICE] Sending metadata")
            self.sendMessage(readFile(metafile, "rb"))
            content = self.readMessage(334, isMetadata=True)
            print("[DEVICE] Got metadata content")
            print("[DEVICE] Metadata content received:", content)
            # returns list = [symmetric-key, digest, nonce]
            return content.split(CNT)
        else:
            print("[DEVICE] Error: Decryption key not received")
            return None
