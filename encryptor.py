from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import os
from utils import *
from constants import *


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
    content = symmetric_key + b'\n' + digest + b'\n' + nonce
    print("[ENC] Metadata content to encrypt:", content)
    ciphertext = cipher_rsa.encrypt(content)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    writeToFile(metadataFile, ciphertext, "wb")
