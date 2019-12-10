from Menu import Menu
from constants import *
from utils import *
from encryptor import *
import fileinput
import sys
import os


def resolveKeyInitMenu(menu, key, btManager):
    if key == 0:
        connectDevice(btManager)
        return menu
    
    else:
        success = checkDeviceConnected(btManager)
        if not success:
            return menu
        getDevice(btManager)
        if key == 1:
            return Menu(ENCRYPT_FILE_WITH_DEVICE_MENU, options=getEncryptableFiles(btManager),
                        resolve_key_function=resolveKeyEncryptMenu)
        elif key == 2:
            return Menu(OPEN_FILE_MENU, options=getOpenableFiles(btManager), resolve_key_function=resolveKeyOpenFileMenu)
        elif key == 3:
            return Menu(SHARE_FILE_MENU, options=getEncryptableFiles(btManager), resolve_key_function=resolveKeyShareFileMenu)                 




def resolveKeyShareFileMenu(menu, key, btManager):
    # show sub-menu asking what files to share with which devices
    active_device = btManager.active_device
    submenu = Menu(DEVICES_MENU, options=btManager.getAllConnectedDevicesIDExcept(active_device), add_return=False, resolve_key_function=resolveShareDeviceMenu)
    list_keys = submenu.show(multiple=True)
    share_devices = submenu.resolveKey(list_keys, btManager)

    # devices to send the share_key after encryption of metadata
    share_devices.append(active_device)

    # file to encrypt
    filename = getFileName(key, getEncryptableFiles(btManager))

    if active_device.isConnected():       
        encryptFileWithManyDevices(filename, share_devices)
    else:
        print("[MENU] Device is not connected")
        
    return Menu(INIT_MENU, options=INIT_MENU_OPTIONS, add_return=False, resolve_key_function=resolveKeyInitMenu)




def resolveKeyEncryptMenu(menu, key, btManager):
    filename = getFileName(key, getEncryptableFiles(btManager))
    device = btManager.active_device
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


def submenuUnlink(btManager):
    # show sub-menu asking if user wants to unlink forever or not
    submenu = Menu(UNLINK_FOR_EVER_MENU, options=UNLINK_FOR_EVER_MENU_OPTIONS, add_return=False, resolve_key_function=resolveUnlinkSubMenu)
    key = submenu.show()
    return submenu.resolveKey(key, btManager)

def resolveKeyOpenFileMenu(menu, key, btManager):
    filename = getFileName(key, getOpenableFiles(btManager))
    device = btManager.active_device

    unlink = submenuUnlink(btManager)

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
                if l_filename == filename and l_ebit.startswith('E'):
                # if l_addr == device.addr and l_filename == filename and l_ebit.startswith('E'):
                    line = line.replace('|E', '|D')
                    changed_bit = True
                
                if (not changed_bit) or (changed_bit and not unlink):
                    newlines.append(line)
                
                if changed_bit and unlink:
                    basefile = l_filename.split("/")[-1]
                    meta_basefile = "metadata-" + (l_addr
                    ).replace(":","-") + "." + basefile
                    metadata_name = "/".join(l_filename.split("/")[:-1]) + "/" + meta_basefile
                    os.remove(metadata_name) 

                changed_bit = False


            writeToFile(LINKEDFILES, ''.join(newlines), 'w')
            print('[MENU] Changed LINKEDFILES encryption bit to: D')
            return menu

    print("[MENU] File is public")
    print("[MENU] Content:", ' '.join(readFile(filename, "r")))
    return menu


# basic
def resolveUnlinkSubMenu(menu, key, btManager):
    # means to unlink
    return key == 1


# advanced version
def getDevice(btManager):
    # show sub-menu asking which device to use
    submenu = Menu(DEVICES_MENU, options=btManager.getAllConnectedDevicesID(), add_return=False, resolve_key_function=resolveDeviceMenu)
    key = submenu.show()
    btManager.active_device = submenu.resolveKey(key, btManager)


def resolveShareDeviceMenu(menu, key, btManager):
    return btManager.connectedDevicesExceptGetIndexs(btManager.active_device, key)

def resolveDeviceMenu(menu, key, btManager):
    return btManager.connectedDevices(key)