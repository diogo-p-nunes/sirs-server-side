# message splitters and concatenators
CNT = b'||'
TSMP = b'|T|'
SIGN = b'|S|'

# variables
FILE_SYSTEM = "server-file-system/"
DATABASES = "databases/"
REGISTERED_DEVICES = DATABASES+"registereddevices.txt"
PUKDIR = "./pukdir"
LINKEDFILES = DATABASES + "filedevicelinks.txt"

# Error messages
INVALID_OPTION = "Invalid option. Enter again."
NO_DEVICE = "No device connected. Connect a device first."

# Menus and their options
INIT_MENU = "========= MAIN MENU ==========\n"
INIT_MENU_OPTIONS = ["Connect device", "Encrypt file with device", "Open file"]
CONNECT_DEVICE_MENU = "========== CONNECT DEVICE =========\n"
ENCRYPT_FILE_WITH_DEVICE_MENU = "======= ENCRYPT FILE WITH DEVICE =======\n"
OPEN_FILE_MENU = "=========== OPEN FILE =========\nSelect one of the files\n"
