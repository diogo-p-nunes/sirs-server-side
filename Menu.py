from constants import *


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
            answer = eval((input("Enter choice: ")))
            if answer != -1 and self.options is None:
                invalid = True
                print(INVALID_OPTION)
            elif self.addReturn and answer == -1:
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

    def setOptions(self, options):
        self.options = options