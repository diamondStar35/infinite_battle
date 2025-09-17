from .sound import *
from .sound_positioning import *
from .soundpool import *

from sound_lib import output

generic_output = None  # used for sounds objects.


generic_output = (
	output.Output()
	)  # initializing default output because the 3d one doesnt work.
generic_output.start()

def quit(self):
	global generic_output
	generic_output.stop()
	generic_output = None