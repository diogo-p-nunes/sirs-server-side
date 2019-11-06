from constants import *


def resolve_key_init_menu(key):
	if key == 0:
		return Menu(CONNECT_DEVICE, addReturn=True)
	elif key == 1:
		return Menu(ENCRYPT_FILE_WITH_DEVICE, addReturn=True)
	elif key == 2:
		return Menu(OPEN_FILE, addReturn=True)

class Menu:
	def __init__(self, text, options=None, addReturn=False, resolve_key_function=None):
		self.text = text
		self.options = options
		self.addReturn = addReturn
		self.resolve_key_function = resolve_key_function
	
	def show(self):
		# display menu information and options if any
		print(self.text)
		if self.addReturn:
			print("-1) Go back")
		if self.options:
			for i, option in enumerate(self.options):
				print(str(i) + ')', option)
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
		print()
		return answer

	def resolve_key(self, key):
		# custom handle of user answer
		# does something specific and returns some menu
		return self.resolve_key_function(key)
