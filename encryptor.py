from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os
from utils import *
from constants import *
from time import sleep


def encryptFile(filename, symmetric_key, nonce = get_random_bytes(15)):
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
    print("content:", content)
    print("[ENC] Wrote decrypted content to file")
    return


def encryptMetadata(filename, symmetric_key, digest, nonce, device):
    print("[ENC] Symm key:", symmetric_key)
    puk = RSA.import_key(open(device.getPukFilename()).read())
    cipher_rsa = PKCS1_OAEP.new(puk)
    content = symmetric_key + CNT + digest + CNT + nonce
    print("[ENC] Metadata content to encrypt:", content)
    ciphertext = cipher_rsa.encrypt(content)

    parts = filename.split("/")
    base = '/'.join(parts[:-1])
    metadataFile = base + "/metadata-" + (device.addr).replace(":", "-") + "." + parts[-1]
    print("[ENC] Created metadata file")
    writeToFile(metadataFile, ciphertext, "wb")


def encryptFileWithDevice(filename, device):
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest, nonce = encryptFile(filename, symmetric_key)
    print("[MENU] Encrypted file with symmetric key")
    encryptMetadata(filename, symmetric_key, digest, nonce, device)
    print("[MENU] Encrypted metadata file with device PUK")
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")


# advanced version
def encryptFileWithManyDevices(filename, devices):
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest, nonce = encryptFile(filename, symmetric_key)
    for d in devices:
        encryptMetadata(filename, symmetric_key, digest, nonce, d)
        print("[MENU] Encrypted metadata file with device PUK")
        writeToFile(LINKEDFILES, d.addr + "|" + filename + "|E" + "\n", "a")
    
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")

def encryptFileWithManyDevicesExtra(filename, devices):
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest, nonce = encryptFile(filename, symmetric_key)
    for d in devices:
        encryptMetadata(filename, symmetric_key, digest, nonce, d)
        print("[MENU] Encrypted metadata file with device PUK")
    
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")

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
    private, shared = getPrivateAndSharedFiles()
    allLinkedFiles = readFile(LINKEDFILES, 'r')

    newlines = []
    if shutting_down:
        for d in devices:
            d.socket = None
    for device in devices:
        if (not device.isConnected() and not device.doneConfAssurance):
            print("[CONFASS] Device %s disconnected." % device.addr)
            print("[CONFASS] Performing Conf-Assurance.")
            for lf in allLinkedFiles:
                l_addr, l_filename, l_ebit = lf.replace('\n', '').split('|')
                if l_addr == device.addr and l_filename in private and l_ebit == 'D':
                    # encrypt file again
                    print("[CONFASS] Encrypting file:", l_filename)
                    encryptFileWithDevice(l_filename, device)
                    lf = lf.replace('|D', '|E')
                    print("[CONFASS] File %s done." % l_filename)
                if lf not in newlines and l_filename not in shared.keys(): newlines.append(lf)
            
            for fs, share_addr in shared.items():
                anyIsConnected = False
                share_devices = [d for d in devices if d.addr in share_addr]
                    
                for ds in share_devices:
                    if ds.isConnected():
                        anyIsConnected = True
                        break
                
                if anyIsConnected:
                    for ds in share_devices:
                        flag = False
                        for lune in allLinkedFiles:
                            l_addr, l_filename, l_ebit = lune.replace('\n', '').split('|')
                            if l_addr == device.addr and l_filename == fs and l_ebit == 'D':
                                flag = True
                                break
                        
                        if flag:
                            lf = ds.addr + "|" + fs + "|D" + "\n"
                        else:
                            lf = ds.addr + "|" + fs + "|E" + "\n"
                            
                        if lf not in newlines: 
                            newlines.append(lf)
                else:
                    #print("share devices:", share_devices, share_addr)
                    flag = False
                    for lune in allLinkedFiles:
                        l_addr, l_filename, l_ebit = lune.replace('\n', '').split('|')
                        if l_addr == device.addr and l_filename == fs and l_ebit == 'D':
                            flag = True
                            break
                    
                    if flag:
                        encryptFileWithManyDevicesExtra(fs, share_devices)
                    for ds in share_devices:
                        lf = ds.addr + "|" + fs + "|E" + "\n"
                        if lf not in newlines: newlines.append(lf)

            device.setDoneConfAssurance(True)
            #devices.remove(device)

    if len(newlines) != 0: writeToFile(LINKEDFILES, ''.join(newlines), 'w')
    #print("private:", private)
    #print("shared:", shared)


# intermediate version
def verifySignature(original, bsign, puk_filename):
    key = RSA.import_key(open(puk_filename).read())
    h = SHA256.new(original)
    try:
        pkcs1_15.new(key).verify(h, bsign)
        return True
    except (ValueError, TypeError):
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