from constants import *
from encryptor import *
from utils import *


def resolveKeyInitMenu(menu, key, btManager):
    if key == 0:
        connectDevice(btManager)
        return menu
    elif key == 1:
        return Menu(ENCRYPT_FILE_WITH_DEVICE_MENU, options=os.listdir(FILE_SYSTEM),
                    resolve_key_function=resolveKeyEncryptMenu)
    elif key == 2:
        return Menu(OPEN_FILE_MENU, options=os.listdir(FILE_SYSTEM), resolve_key_function=resolveKeyOpenFileMenu)


def resolveKeyEncryptMenu(menu, key, btManager):
    filename = getFileName(key)
    if not btManager.hasConnectedDevices():
        print("[MENU] No device connected :(")
    else:
        # show list of user devices to select from once we implement multiple devices
        # for now just get the only connected device
        device = btManager.getDevice()
        print("[MENU] Got device")
        symmetric_key = generateSymmKey()
        print("[MENU] Generated symmetric key")
        encryptFile(filename, symmetric_key)
        print("[MENU] Encrypted file with symmetric key")
        encryptSymmInMetadata(filename, symmetric_key, device.getPuk())
        print("[MENU] Encrypted metadata file with device PUK")
        # trash symmetric_key variable
        print("[MENU] Deleted symmetric key")
        print("File encrypted with device.")
    return menu


def resolveKeyOpenFileMenu(menu, key, btManager):
    filename = getFileName(key)
    print("Pre-decryption:")
    openFile(filename)
    symmetric_key = requestDecryptionKey(filename)
    decryptFile(filename, symmetric_key)
    print("\nPost-decryption:")
    openFile(filename)
    return menu


class Menu:
    def __init__(self, text, options=None, add_return=True, resolve_key_function=None):
        self.text = text
        self.options = options
        self.addReturn = add_return
        self.resolve_key_function = resolve_key_function

    def show(self):
        # display menu information and options if any
        print("\n\n" + self.text)
        if self.addReturn:
            print("-1) Go back")
        if self.options:
            for i, option in enumerate(self.options):
                print(' ' + str(i) + ')', option)
        print("=" * len(self.text.split("\n")[0]))
        # get user answer - if invalid display again
        invalid = True
        answer = None
        while invalid:
            answer = eval(input("Enter choice: "))
            if self.addReturn and answer == -1:
                invalid = False
            elif answer in range(len(self.options)):
                invalid = False
            else:
                print(INVALID_OPTION)
        # return user answer
        return answer

    def resolveKey(self, key, btManager):
        # custom handle of user answer
        # does something specific and returns some menu
        return self.resolve_key_function(self, key, btManager)
