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
    with open(filename, 'wb') as f:
        f.write(ciphertext)

    #print("digest:", digest)
    #cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    #content = cipher.decrypt_and_verify(ciphertext, digest)
    #print("[ENCRYPT DECRYPT]", content.decode())
    return digest, nonce


def generateSymmKey(bytes=16):
    random_key = os.urandom(bytes)
    return random_key


def decryptFile(filename, symmetric_key):
    print("[ENC] Symm key:", symmetric_key)
    # print("digest:", digest)
    # cipher = AES.new(symmetric_key, AES.MODE_EAX, nonce=nonce)
    # content = cipher.decrypt_and_verify(ciphertext, digest)
    # print("[ENCRYPT DECRYPT]", content.decode())
    # writeToFile(filename, content, "wb")
    return


def encryptSymmInMetadata(filename, symmetric_key, pukFile):
    print("[ENC] Symm key:", symmetric_key)
    puk = RSA.import_key(open(pukFile).read())
    cipher_rsa = PKCS1_OAEP.new(puk)

    # cipher_rsa = PKCS1_v1_5.new(puk)
    # enc_sym_key = cipher_rsa.encrypt(symmetric_key)

    enc_sym_key = cipher_rsa.encrypt(symmetric_key)
    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    with open(metadataFile, 'wb') as f:
        f.write(enc_sym_key)
