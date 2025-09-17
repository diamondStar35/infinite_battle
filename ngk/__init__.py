import pygame
import platform
import sys
import os
from pygame.locals import *
from . import snd
from . import ui
from .dlg import *
from .output import *
from .packfile import *
from .timer import *
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
window = None
running = False
_resource_file = None
current_key_pressed = -1
current_key_released = -1
old_keys_held = []
keys_held = []
f4key = False
altkey = False

def init():
	global running
	pygame.init()
	from pygame import locals
	running=True
def quit():
	pygame.quit()
def show_window(title="test",size=(640,480)):
	global window
	window=pygame.display.set_mode(size)
	pygame.display.set_caption(title)
	return window
def process():
	global current_key_pressed, current_key_released, old_keys_held, keys_held, running, window, altkey, f4key
	current_key_pressed = -1
	current_key_released = -1
	old_keys_held = keys_held
	events = pygame.event.get()
	for event in events:
		if event.type == QUIT:
			running = False
			quit()
			sys.exit(0)
			break
		# update key state here
		keys_held = ()
		keys_held = pygame.key.get_pressed()
		if event.type == pygame.KEYDOWN:
			if platform.system() == "Windows": # check for alt f4
				if event.key==pygame.K_RALT or event.key==pygame.K_LALT:
					altkey=True
				elif event.key==pygame.K_F4:
					f4key=True
			if len(old_keys_held) > 0 and old_keys_held[event.key] == False:
				current_key_pressed = event.key
		if event.type == pygame.KEYUP:
			if platform.system() == "Windows": # check for alt f4
				if event.key==pygame.K_RALT or event.key==pygame.K_LALT:
					altkey=False
				elif event.key==pygame.K_F4:
					f4key=False
			current_key_released = event.key
	if altkey and f4key:
		running = False
		quit()
		sys.exit()
	pygame.display.update()
	return events
def key_pressed(key_code):
	"""Checks if a key was pressed down this frame (single key press)
	* key_code: A pygame.K_ key code
	
	returns: True if the specified key kode was pressed, False otherwise.
	"""
	global current_key_pressed
	return current_key_pressed == key_code


def key_released(key_code):
	"""Checks if a key was released down this frame (single key release)
	* key_code: A pygame.K_ key code
	
	returns: True if the specified key kode was released, False otherwise.
	"""
	global current_key_released
	return current_key_released == key_code


def key_down(key_code):
	"""Checks if a key is beeing held down.
	* key_code: A pygame.K_ key code
	
	returns: True if the specified key kode is beeing held down, False otherwise.
	"""
	global keys_held
	return keys_held[key_code]


def key_up(key_code):
	"""Check if a key isn't beeing held down (ie if it's not pressed and held)
	* key_code : A pygame.K_ key code
	
	returns: True if key is not held down, False otherwise
	"""
	global keys_held
	return keys_held[key_code] == False
def get_global_resource_file():
	global _resource_file
	return _resource_file
def set_global_resource_file(file):
	global _resource_file
	if not isinstance(file, ResourceFile):
		raise ValueError('"file" must be an instance of "ngk.ResourceFile".')
	_resource_file = file