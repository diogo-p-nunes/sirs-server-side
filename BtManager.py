from bluetooth import PORT_ANY, BluetoothSocket, RFCOMM, advertise_service, SERIAL_PORT_CLASS, SERIAL_PORT_PROFILE
from utils import writeToFile
from Device import Device
from constants import *


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

        # add the just connected device to the list of connected devices

        # first check if it had been connected before
        for device in self.connected_devices:
            if device.addr == device_addr[0]:
                device.socket = device_socket
                device.doneConfAssurance = False
                return device

        # if it had never been connected before
        device = Device(device_socket, device_addr[0])
        self.connected_devices.append(device)
        return device

    def hasConnectedDevices(self):
        # if at least one device is connected returns true else false
        return len(self.connected_devices) > 0

    def isDeviceRegistered(self, device):
        with open(REGISTERED_DEVICES, 'r') as f:
            for entry in f:
                addr, puk_filename = entry.split("|")
                # print("Reading entry:", addr, puk)
                if addr == device.addr:
                    device.sendMessage("OK")
                    device.setPukFilename(puk_filename[:-1])
                    return True
            device.sendMessage("NO")
            return False

    def registerDevice(self, device):
        print("[BT] Registering device ...")
        writeToFile(REGISTERED_DEVICES, device.getRegistrationEntry() + "\n", 'a')
        device.sendMessage("OK")
        print("[BT] Device Registered")
        return True

    def getDevice(self, index=-1):
        if self.hasConnectedDevices():
            return self.connected_devices[-1]
        else:
            return None
