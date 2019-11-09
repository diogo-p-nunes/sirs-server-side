from bluetooth import PORT_ANY, BluetoothSocket, RFCOMM, advertise_service, SERIAL_PORT_CLASS, SERIAL_PORT_PROFILE
from constants import *
from main import *
from encryptor import *
import subprocess


def openFile(filename):
    command = "cat " + filename
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)




def connectDevice(btManager):
    if btManager.connect():
        if not btManager.isDeviceRegistered():
            print("Registering Device...")
            btManager.register()
        print("Device Connected")



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
    if not btManager.isConnected():
        print("You're not connected :(")
    else:
        symmetric_key = generateSymmKey()
        encryptFile(filename, symmetric_key)
        # generate metadata file
        print(symmetric_key)
        encryptSymmInMetadata(filename, symmetric_key, btManager.getPuk())
        # encrypt metadata file with device public key
        # trash symmetric_key variable
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

    def resolveKey(self, key, btManager):
        # custom handle of user answer
        # does something specific and returns some menu
        return self.resolve_key_function(self, key, btManager)


class BtManager:
    def __init__(self):
        self.device_socket = None
        self.server_socket = None
        self.device_addr = None
        self.puk = None

    def connect(self, uuid="1e0ca4ea-299d-4335-93eb-27fcfe7fa848"):
        self.server_socket = BluetoothSocket(RFCOMM)
        self.server_socket.bind(("", PORT_ANY))
        self.server_socket.listen(1)

        port = self.server_socket.getsockname()[1]

        advertise_service(self.server_socket, "FeelingBlue",
                          service_id=uuid,
                          service_classes=[uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE], )

        print("[BT] Waiting for device connection at %d " % port)

        self.device_socket, self.device_addr = self.server_socket.accept()
        print("[BT] Accepted connection from ", self.device_addr)
        return True

    def isConnected(self):
        if self.device_addr is None and self.device_socket is None:
            return False
        else:
            return True

    def isDeviceRegistered(self):
        if self.isConnected():
            #print("Is connected")
            with open(REGISTERED_DEVICES, 'r') as f:
                for entry in f:
                    addr, puk = entry.split("|")
                    #print("Readinge entry:", addr, puk)
                    if addr == self.device_addr[0]:
                        self.sendMessage("OK")
                        self.puk = puk
                        return True
                self.sendMessage("NOK")
                return False
        else:
            return False

    def register(self):
        puk = self.requestDevicePuk()
        if puk is None:
            #print("puk is None")
            return False
        with open(REGISTERED_DEVICES, 'w+') as f:
            f.write(self.device_addr[0] + "|" + puk.decode("utf-8"))
            #print("addr added")
        self.sendMessage("OK")
        print("Device Registered!")
        return True



    def requestDevicePuk(self, pukbytes=3):
        #ask data from android
        #return data
        #print("Requesting Puk")
        try:
            data = self.device_socket.recv(pukbytes)
            if len(data) == 0: return None
            #print("received [%s]" % data)
        except IOError:
            #print("Puk not received")
            return None
        return data

    def sendMessage(self, m):
        self.device_socket.send(m)

    def getPuk(self):
        return self.puk
