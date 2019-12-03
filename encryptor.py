from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os
from utils import writeToFile, readFile
from constants import *
from time import sleep


def encryptFile(filename, symmetric_key):
    nonce = get_random_bytes(15)
    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    ciphertext, digest = cipher.encrypt_and_digest(readFile(filename, "rb"))
    writeToFile(filename, ciphertext, "wb")
    return digest, nonce


def generateSymmKey(bytes=16):
    random_key = os.urandom(bytes)
    return random_key


def decryptFile(filename, symmetric_key, digest, nonce):
    print("[ENC] Symm key:", symmetric_key)
    ciphertext = readFile(filename, "rb")
    cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    content = cipher.decrypt_and_verify(ciphertext, digest)
    print("[ENC] Decrypted content")
    writeToFile(filename, content, "wb")
    print("[ENC] Wrote decrypted content to file")
    return


def encryptMetadata(filename, symmetric_key, digest, nonce, pukFile):
    print("[ENC] Symm key:", symmetric_key)
    puk = RSA.import_key(open(pukFile).read())
    cipher_rsa = PKCS1_OAEP.new(puk)
    content = symmetric_key + CNT + digest + CNT + nonce
    print("[ENC] Metadata content to encrypt:", content)
    ciphertext = cipher_rsa.encrypt(content)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    writeToFile(metadataFile, ciphertext, "wb")


def encryptFileWithDevice(filename, device):
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest, nonce = encryptFile(filename, symmetric_key)
    print("[MENU] Encrypted file with symmetric key")
    encryptMetadata(filename, symmetric_key, digest, nonce, device.getPukFilename())
    print("[MENU] Encrypted metadata file with device PUK")
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")


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


# intermediate version
def addSignature(m,original):
    print("+ signature")
    return m+SIGN+messageSignature(original)


# intermediate version
def messageSignature(original):
    #priv = RSA.import_key(open("private_key.pem").read())
    priv = RSA.importKey(open("CA_keys/private.key").read())
    h = SHA256.new(original)
    return pkcs1_15.new(priv).sign(h)


# advanced version
def threadedCheckIfDisconnected(btManager, run_event):
    while run_event.is_set():
        devices = btManager.connected_devices
        #if len(devices) == 0:
        #    print("[CONFASS] No devices connected.")
        confAssurance(devices)
        sleep(5)



def confAssurance(devices):
    for device in devices:
        if not device.isConnected() and not device.doneConfAssurance:
            print("[CONFASS] Device %s disconnected." % device.addr)
            print("[CONFASS] Performing Conf-Assurance.")

            # check if file was decrypted by the device in this session
            lines = readFile(LINKEDFILES, 'r')
            newlines = []
            for line in lines:
                l_addr, l_filename, l_ebit = line.replace('\n', '').split('|')
                if l_addr == device.addr and l_ebit == 'D':
                    # encrypt file again
                    print("[CONFASS] Encrypting file:", l_filename, end='')
                    encryptFileWithDevice(l_filename, device)
                    line = line.replace('|D', '|E')
                    print(" ... done.")
                newlines.append(line)

            writeToFile(LINKEDFILES, ''.join(newlines), 'w')
            device.setDoneConfAssurance(True)