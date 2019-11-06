import Cryptodome
from constants import *
from utils import *

"""
Main function.

Description:
Write someting here
"""
if __name__ == "__main__":

	# start with initial menu
	menu = Menu(INIT_MENU, options=INIT_MENU_OPTIONS, resolve_key_function=resolve_key_init_menu)
	while True:
		key = menu.show()
		if key != -1:
			menu = menu.resolve_key(key)