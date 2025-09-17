from accessible_output2.outputs.auto import*
output=Auto()
def speak(text,interrupt=False):
	output.speak(text,interrupt)
def stop_speech():
	output.silence()
def  braille(text):
	output.braille(text)