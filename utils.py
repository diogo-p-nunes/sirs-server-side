from constants import *
import os
from encryptor import *
import subprocess


def openFile(filename):
    command = "cat " + filename
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)


def resolveKeyInitMenu(menu, key):
    if key == 0:
        return Menu(CONNECT_DEVICE_MENU)
    elif key == 1:
        return Menu(ENCRYPT_FILE_WITH_DEVICE_MENU, options=os.listdir(FILE_SYSTEM),
                    resolve_key_function=resolveKeyEncryptMenu)
    elif key == 2:
        return Menu(OPEN_FILE_MENU, options=os.listdir(FILE_SYSTEM), resolve_key_function=resolveKeyConnectMenu)


def resolveKeyEncryptMenu(menu, key):
    filename = getFileName(key)
    # device = getConnectedDevice()
    # device = None
    # if not device:
    #    print(NO_DEVICE)
    #    return menu
    symmetric_key = generateSymmKey()
    encryptFile(filename, symmetric_key)
    # generate metadata file
    # encrypt metadata file with device public key
    # trash symmetric_key variable
    print("File encrypted with device.")


def resolveKeyConnectMenu(menu, key):
    filename = getFileName(key)

    print("Pre-decryption:")
    openFile(filename)

    symmetric_key = requestDecryptionKey(filename)
    decryptFile(filename, symmetric_key)

    print("\nPost-decryption:")
    openFile(filename)
    return menu


def getFileName(key):
    return os.getcwd() + "/" + FILE_SYSTEM + os.listdir(FILE_SYSTEM)[key]


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

    def resolveKey(self, key):
        # custom handle of user answer
        # does something specific and returns some menu
        return self.resolve_key_function(self, key)
