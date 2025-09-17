import time


class Timer:
	def __init__(self):
		self.inittime = time.time()
		self.paused = 0

	@property
	def elapsed(self):
		if self.paused != 0:
			return self.paused
		else:
			return self._ms(time.time() - self.inittime)

	@elapsed.setter
	def elapsed(self, amount):
		if self.paused == 0:
			self.inittime = time.time() - (amount / 1000)
		else:
			self.paused = amount

	def restart(self):
		self.__init__()

	def pause(self):
		self.paused = self._ms(time.time() - self.inittime)

	def resume(self):
		self.inittime = time.time() - (self.paused / 1000)
		self.paused = 0

	def _ms(self, t):
		return int(round(t*1000))
