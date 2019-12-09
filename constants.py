# message splitters and concatenators
CNT = b'|S|'
TSMP = b'|X|'
SIGN = b'|X|'

# variables
FILE_SYSTEM = "server-file-system/"
DATABASES = "databases/"
REGISTERED_DEVICES = DATABASES+"registereddevices.txt"
PUKDIR = "./pukdir"
LINKEDFILES = DATABASES + "filedevicelinks.txt"
CAKEYS = "CA_keys/"

# Error messages
INVALID_OPTION = "Invalid option. Enter again."
NO_DEVICE = "No device connected. Connect a device first."

# Menus and their options
INIT_MENU = "========= MAIN MENU ==========\n"
INIT_MENU_OPTIONS = ["Connect device", "Encrypt file with device", "Open file", "Share file"]
CONNECT_DEVICE_MENU = "========== CONNECT DEVICE =========\n"
ENCRYPT_FILE_WITH_DEVICE_MENU = "======= ENCRYPT FILE WITH DEVICE =======\n"
OPEN_FILE_MENU = "=========== OPEN FILE =========\nSelect one of the files\n"
UNLINK_FOR_EVER_MENU = "============ (UN)LINK FROM DEVICE =============\n"
UNLINK_FOR_EVER_MENU_OPTIONS = ["Open only in this session (maintain link)", "Make file public (unlink)"]
DEVICES_MENU = "============ SELECT A DEVICE =============\n"
SHARE_FILE_MENU = "============= SELECT FILE TO SHARE ===========\nSelect one of the files\n"