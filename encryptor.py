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


def encryptMetadataWithSymmetric(filename, symmetric_key, digest_file, nonce_file, share_key):
    # content from the share file that was encrypted
    content = symmetric_key + CNT + digest_file + CNT + nonce_file
    print("[ENC] Metadata content to encrypt:", content)

    nonce = get_random_bytes(15)
    cipher = AES.new(share_key, AES.MODE_EAX, nonce=nonce)
    ciphertext, digest = cipher.encrypt_and_digest(content)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata." + parts[-1]
    print("[ENC] Created metadata file")
    writeToFile(metadataFile, ciphertext, "wb")
    return digest, nonce


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


#advanced version
def encryptFileWithManyDevices(filename, devices, share_key):
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest_file, nonce_file = encryptFile(filename, symmetric_key)
    print("[MENU] Encrypted file with share key")
    digest_metadata, nonce_metadata = encryptMetadataWithSymmetric(filename, share_key, digest_file, nonce_file, share_key)
    print("[MENU] Encrypted metadata file with device ShareKey") 
    for d in devices:     
        writeToFile(LINKEDFILES, d.addr + "|" + filename + "|E" + "\n", "a")
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")
    return digest_metadata, nonce_metadata

# intermediate version
def addTimestamp(m):
    timestamp = str(datetime.datetime.utcnow())
    return m + TSMP + timestamp.encode()


# intermediate version
def addSignature(m):
    return m + SIGN + messageSignature(m)


# intermediate version
def messageSignature(original):
    priv = RSA.importKey(open("CA_keys/private.key").read())
    h = SHA256.new(original)
    return pkcs1_15.new(priv).sign(h)


# advanced version
def threadedCheckIfDisconnected(btManager, run_event):
    while run_event.is_set():
        devices = btManager.connected_devices
        confAssurance(devices)
        sleep(5)


# advanced version
def confAssurance(devices, shutting_down=False):
    for device in devices:
        if (not device.isConnected() and not device.doneConfAssurance) or shutting_down:
            print("[CONFASS] Device %s disconnected." % device.addr)
            print("[CONFASS] Performing Conf-Assurance.")

            # check if file was decrypted by the device in this session
            lines = readFile(LINKEDFILES, 'r')
            newlines = []
            for line in lines:
                l_addr, l_filename, l_ebit = line.replace('\n', '').split('|')
                if l_addr == device.addr and l_ebit == 'D':
                    # encrypt file again
                    print("[CONFASS] Encrypting file:", l_filename)
                    encryptFileWithDevice(l_filename, device)
                    line = line.replace('|D', '|E')
                    print("[CONFASS] File %s done." % l_filename)

                newlines.append(line)

            writeToFile(LINKEDFILES, ''.join(newlines), 'w')
            device.setDoneConfAssurance(True)
            devices.remove(device)


# intermediate version
def verifySignature(original, bsign, puk_filename):
    key = RSA.import_key(open(puk_filename).read())
    h = SHA256.new(original)
    try:
        pkcs1_15.new(key).verify(h, bsign)
        print("The signature is valid.")
        return True
    except (ValueError, TypeError):
        print("The signature is not valid.")
        return False


# intermediate version
def verifyTimeStamp(btimestamp): #recebe byte array de timestamp
    now = datetime.datetime.utcnow()
    timestamp = datetime.datetime.strptime(btimestamp.decode('utf-8'), '%Y-%m-%d %H:%M:%S')
    timeStampValidity = timestamp + datetime.timedelta(seconds=10)
    if now < timeStampValidity:
        return True
    else:
        return False

#advanced version
def sendShareKey(share_key, digest_metadata, nonce_metadata, pukFile, device):
    device.sendMessage("RS")
    puk = RSA.import_key(open(pukFile).read())
    cipher_rsa = PKCS1_OAEP.new(puk)
    content = share_key + CNT + digest_metadata + CNT + nonce_metadata
    print("[ENC] Encrypting sharekey+digest+nonce for metadata of shared file:", content)
    ciphertext = cipher_rsa.encrypt(content)
    print("[ENC] Done encrypting share metadata")
    print("[ENC] Sending share metadata")
    device.sendMessage(ciphertext)