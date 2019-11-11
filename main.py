
from constants import *
from utils import *
from BTManager import *
from MenuManager import *


"""
Main function.

Description:
Write something here
"""
if __name__ == "__main__":
    btManager = BtManager()
    menu_navigation = []
    menu = Menu(INIT_MENU, options=INIT_MENU_OPTIONS, add_return=False, resolve_key_function=resolveKeyInitMenu)
    menu_navigation.append(menu)
    while True:
        menu = menu_navigation[-1]
        key = menu.show()
        if key != -1:
            next_menu = menu.resolveKey(key, btManager)
            if menu.text != next_menu.text:
                menu_navigation.append(next_menu)
        else:
            menu_navigation = menu_navigation[:-1]