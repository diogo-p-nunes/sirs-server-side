from Menu import Menu
from BtManager import BtManager
from constants import *
from resolvers import resolveKeyInitMenu
from threading import Thread, Event
from encryptor import threadedCheckIfDisconnected, confAssurance


"""
Main function

Description:
Displays a cycle of menus directed by the users choices.
Additionaly, launch a thread that in parallel from time to time 
checks if there are any devices that were connected during this session
and for some reason disconnected. This is done so the Conf-Assurance protocol
may be performed when a device disconnects.
"""
if __name__ == "__main__":
    try:
        btManager = BtManager()

        # create thread to time to time check if bluetooth devices have disconnected
        run_event = Event()
        run_event.set()

        thread = Thread(target=threadedCheckIfDisconnected, args=(btManager, run_event))
        thread.start()

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

    except KeyboardInterrupt:
        print("[Menu] Shutting down ... ")
        run_event.clear()
        thread.join()
        confAssurance(btManager.connected_devices, shutting_down=True)
        exit()
