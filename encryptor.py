import os

from Cryptodome.Cipher import AES


def getFileData(filename):
    with open(filename, 'r') as f:
        output = f.read()
    return bytearray(output, 'utf-8')


def encryptFile(filename, symmetric_key):
    cipher = AES.new(symmetric_key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(getFileData(filename))
    with open(filename, 'wb') as f:
        f.write(ciphertext)
    return


def generateSymmKey(bits=16):
    random_key = os.urandom(bits)
    return random_key


def requestDecryptionKey(filename):
    return


def decryptFile(filename, symmetric_key):
    return

