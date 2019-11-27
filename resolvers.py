from Menu import Menu
from constants import *
from utils import *
from encryptor import *
import fileinput
import sys


def resolveKeyInitMenu(menu, key, btManager):
    if key == 0:
        connectDevice(btManager)
        return menu
    elif key == 1:
        return Menu(ENCRYPT_FILE_WITH_DEVICE_MENU, options=getEncryptableFiles(btManager),
                    resolve_key_function=resolveKeyEncryptMenu)
    elif key == 2:
        return Menu(OPEN_FILE_MENU, options=getOpenableFiles(btManager), resolve_key_function=resolveKeyOpenFileMenu)


def resolveKeyEncryptMenu(menu, key, btManager):
    filename = getFileName(key, getEncryptableFiles(btManager))
    # show list of user devices to select from once we implement multiple devices
    # for now just get the only connected device
    device = btManager.getDevice()
    print("[MENU] Got device")
    symmetric_key = generateSymmKey()
    print("[MENU] Generated symmetric key")
    digest, nonce = encryptFile(filename, symmetric_key)
    print("[MENU] Encrypted file with symmetric key")
    encryptMetadata(filename, symmetric_key, digest, nonce, device.getPukFilename())
    print("[MENU] Encrypted metadata file with device PUK")
    # trash symmetric_key variable
    del symmetric_key
    print("[MENU] Deleted symmetric key")
    writeToFile(LINKEDFILES, device.addr + "|" + filename + "|E" + "\n", "a")
    print("[MENU] Added file link to databases")
    print("[MENU] File encrypted with device")
    menu.setOptions(getEncryptableFiles(btManager))
    return menu


def resolveKeyOpenFileMenu(menu, key, btManager):
    filename = getFileName(key, getOpenableFiles(btManager))
    device = btManager.getDevice()
    print("[MENU] Got device")
    print("[MENU] Pre-decryption:", readFile(filename, "rb"))
    symmetric_key, digest, nonce = device.requestMetadataContent(filename)
    decryptFile(filename, symmetric_key, digest, nonce)
    print("[MENU] Post-decryption:", readFile(filename, "r"))



    return menu
