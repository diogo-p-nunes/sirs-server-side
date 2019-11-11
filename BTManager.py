from bluetooth import PORT_ANY, BluetoothSocket, RFCOMM, advertise_service, SERIAL_PORT_CLASS, SERIAL_PORT_PROFILE
from constants import *


class Device:
    def __init__(self, socket, addr, puk=None):
        self.socket = socket
        self.addr = addr
        self.puk = puk

    def setPuk(self, puk):
        if type(puk) == str:
            puk = bytes(puk, "utf-8")
        self.puk = puk

    def getPuk(self):
        if self.puk is not None:
            return self.puk
        else:
            # ask data from android
            # print("Requesting Puk")
            try:
                data = self.socket.recv(3)
                if len(data) == 0:
                    return None
                # print("received [%s]" % data)
            except IOError:
                print("[DEVICE] Error: Puk not received")
                return None
            self.setPuk(data)
            return self.getPuk()

    def isConnected(self):
        if self.addr is None and self.socket is None:
            return False
        else:
            return True

    def getRegistrationEntry(self):
        return self.addr + "|" + self.getPuk().decode("utf-8")

    def sendMessage(self, m):
        self.socket.send(m)


class BtManager:
    def __init__(self):
        self.server_socket = None
        self.connected_devices = []

    def connect(self, uuid="1e0ca4ea-299d-4335-93eb-27fcfe7fa848"):
        # only create server socket once
        if self.server_socket is None:
            self.server_socket = BluetoothSocket(RFCOMM)
            self.server_socket.bind(("", PORT_ANY))
            self.server_socket.listen(1)
            advertise_service(self.server_socket, "FeelingBlue",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE], )

        port = self.server_socket.getsockname()[1]
        print("[BT] Waiting for device connection at %d ..." % port)
        device_socket, device_addr = self.server_socket.accept()
        print("[BT] Accepted connection from", device_addr[0])

        # add just connected device to the list of connected devices
        device = Device(device_socket, device_addr[0])
        self.connected_devices.append(device)
        return device

    def hasConnectedDevices(self):
        # if at least one device is connected returns true else false
        return len(self.connected_devices) > 0

    def isDeviceRegistered(self, device):
        with open(REGISTERED_DEVICES, 'r') as f:
            for entry in f:
                addr, puk = entry.split("|")
                # print("Reading entry:", addr, puk)
                if addr == device.addr:
                    device.sendMessage("OK")
                    device.setPuk(puk)
                    return True
            device.sendMessage("NOK")
            return False

    def registerDevice(self, device):
        print("[BT] Registering device ...")
        with open(REGISTERED_DEVICES, 'w+') as f:
            f.write(device.getRegistrationEntry())
        device.sendMessage("OK")
        print("[BT] Device Registered")
        return True

    def getDevice(self, index=-1):
        if self.hasConnectedDevices():
            return self.connected_devices[-1]
        else:
            return None