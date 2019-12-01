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

    # check if file was already decrypted by the device
    lines = readFile(LINKEDFILES, 'r')
    newlines = []
    for line in lines:
        l_addr, l_filename, l_ebit = line.replace('\n', '').split('|')
        if l_addr == device.addr and l_filename == filename and l_ebit == 'D':
            print("[MENU] File already decrypted by device")
            print("[MENU] Post-decryption:", ' '.join(readFile(filename, "r")))
            return menu

        elif l_addr == device.addr and l_filename == filename and l_ebit == 'E':
            print("[MENU] Pre-decryption:", readFile(filename, "rb"))
            symmetric_key, digest, nonce = device.requestMetadataContent(filename)
            decryptFile(filename, symmetric_key, digest, nonce)
            print("[MENU] Post-decryption:", ' '.join(readFile(filename, "r")))

            # change the bit of encryption in the LINKEDFILES database so that we know that this file is decrypted
            lines = readFile(LINKEDFILES, 'r')
            newlines = []
            for line in lines:
                l_addr, l_filename, l_ebit = line.split('|')
                if l_addr == device.addr and l_filename == filename and l_ebit.startswith('E'):
                    line = line.replace('|E', '|D')
                newlines.append(line)

            writeToFile(LINKEDFILES, ''.join(newlines), 'w')
            print('[MENU] Changed LINKEDFILES encryption bit to: D')
            return menu

    print("[MENU] File is public")
    print("[MENU] Content:", ' '.join(readFile(filename, "r")))
    return menu
