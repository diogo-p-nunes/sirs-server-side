# Smartphone as a security token
### Group A27 - SIRS 19/20

The computer application (CA) was developed in Python3 in native Ubuntu 18.04.1 LTS. It was tested in a VM (VirtualBox) but certain features (such as file sharing) depend on the capabilities of the Bluetooth adapter.  
Running with sudo is required.

__Change Bluetooth settings:__  

    $ sudo nano /etc/systemd/system/dbus-org.bluez.service
			Change 'ExecStart=/usr/lib/bluetooth/bluetoothd' to 'ExecStart=/usr/lib/bluetooth/bluetoothd --compat'
    $ sudo systemctl daemon-reload
    $ sudo systemctl restart bluetooth
    $ sudo chmod 777 /var/run/sdp

__Python3 requirements:__  
 
    $ pip3 install pybluez
    $ pip3 install pycryptodome


__Run:__  

If it's the first time (or wish to reset state) first run:

    $ sudo ./init.sh

Run the CA application:

    $ sudo python3 main.py

__ What you should see:__  

    ========= MAIN MENU ==========

     0) Connect device
     1) Encrypt file with device
     2) Open file
     3) Share file
    ==============================
    Enter choice: 