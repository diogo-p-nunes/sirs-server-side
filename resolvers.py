from Menu import Menu
from constants import *
from utils import getEncryptableFiles, connectDevice, getOpenableFiles, getFileName, writeToFile, readFile
from encryptor import encryptFileWithDevice, decryptFile
import fileinput
import sys
import os


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
    #print("[MENU] Got device")
    if device.isConnected():
        encryptFileWithDevice(filename, device)
        writeToFile(LINKEDFILES, device.addr + "|" + filename + "|E" + "\n", "a")
        print("[MENU] Added file link to databases")
        print("[MENU] File encrypted with device")
        menu.setOptions(getEncryptableFiles(btManager))
    else:
        print("[MENU] Device is not connected")
        menu = Menu(INIT_MENU, options=INIT_MENU_OPTIONS, add_return=False, resolve_key_function=resolveKeyInitMenu)

    return menu


def resolveKeyOpenFileMenu(menu, key, btManager):
    filename = getFileName(key, getOpenableFiles(btManager))
    # show list of user devices to select from once we implement multiple devices
    # for now just get the only connected device
    device = btManager.getDevice()
    
    # show sub-menu asking if user wants to unlink forever or not
    submenu = Menu(UNLINK_FOR_EVER_MENU, options=UNLINK_FOR_EVER_MENU_OPTIONS, add_return=False, resolve_key_function=resolveUnlinkSubMenu)
    key = submenu.show()
    unlink = submenu.resolveKey(key, btManager)
    #print("UNLINK:", unlink)

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
            # or remove entry from database if unlink is true
            lines = readFile(LINKEDFILES, 'r')
            newlines = []
            changed_bit = False
            for line in lines:
                l_addr, l_filename, l_ebit = line.split('|')
                if l_addr == device.addr and l_filename == filename and l_ebit.startswith('E'):
                    line = line.replace('|E', '|D')
                    changed_bit = True
                
                if (not changed_bit) or (changed_bit and not unlink):
                    newlines.append(line)
                
                if changed_bit and unlink:
                    basefile = l_filename.split("/")[-1]
                    meta_basefile = "metadata." + basefile
                    metadata_name = "/".join(l_filename.split("/")[:-1]) + "/" + meta_basefile
                    os.remove(metadata_name) 

                changed_bit = False


            writeToFile(LINKEDFILES, ''.join(newlines), 'w')
            print('[MENU] Changed LINKEDFILES encryption bit to: D')
            return menu

    print("[MENU] File is public")
    print("[MENU] Content:", ' '.join(readFile(filename, "r")))
    return menu



def resolveUnlinkSubMenu(menu, key, btManager):
    # means to unlink
    return key == 1

