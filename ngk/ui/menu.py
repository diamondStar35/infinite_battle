import ngk
import pygame
class menu_item:
	def __init__(self,name,ref="",disabled=False):
		self.name=name
		self.reference=ref
		if self.reference==None:
			self.reference=Name
		self.disabled=disabled
class m_pro:
	def  __init__(self):
		self.p=ngk.snd.SoundPool()
		self.running=False
		self.callback=None
		self.music_added=False
		self.repeat_at_edge=True
		self.wrap=True
		self.musictimer=ngk.Timer()
		self.click_sound=""
		self.edge_sound=""
		self.enter_sound=""
		self.open_sound=""
		self.cursor=-1
		self.music=ngk.snd.Sound()
		self.items=[]
	def add_item_tts(self,name,ref,disabled=False):
		self.items.append(menu_item(name,ref,disabled))
	def add_music(self,path):
		if self.music.handle==None or self.music.handle.is_playing==False:
			self.music.load(path)
			self.music_added=True
			self.music.volume=-10
	def play_music(self):
		if self.music.handle.is_playing==False and self.music_added==True:
			self.music.play_looped()
	def reset(self,clear_all=True):
		if clear_all==True:
			self.click_sound=""
			self.edge_sound=""
			self.enter_sound=""
			self.music_added=False
			self.music.close()
		self.items.clear()
		self.cursor=-1
	def play_click_sound(self):
		if self.click_sound!="": self.p.play_stationary(self.click_sound,False)
	def play_edge_sound(self):
		if self.edge_sound!="": self.p.play_stationary(self.edge_sound,False)
	def play_enter_sound(self):
		if self.enter_sound!="": self.p.play_stationary(self.enter_sound,False)
	def speak_item(self):
		ngk.speak(self.items[self.cursor].name)
	def run(self,intro=""):
		if self.music_added==True:
			self.play_music()
		ngk.speak(intro)
		self.running=True
		while self.running==True:
			ngk.process()
			pygame.time.wait(5)
			if callable(self.callback): self.callback(self)
			if ngk.key_pressed(pygame.K_DOWN):
				if self.cursor==len(self.items)-1:
					if self.wrap==True:
						self.play_click_sound()
						self.cursor=0
						self.speak_item()
					else:
						self.play_edge_sound()
						if self.repeat_at_edge==True: self.speak_item()
				else:
					self.play_click_sound()
					self.cursor+=1
					self.speak_item()
			if ngk.key_pressed(pygame.K_UP):
				if self.cursor==-1:
					self.play_click_sound()
					self.cursor=len(self.items)-1
					self.speak_item()
				elif self.cursor==0:
					if self.wrap==True:
						self.play_click_sound()
						self.cursor=len(self.items)-1
						self.speak_item()
					else:
						self.play_edge_sound()
						if self.repeat_at_edge==True: self.speak_item()
				else:
					self.cursor-=1
					self.play_click_sound()
					self.speak_item()
			if ngk.key_pressed(pygame.K_ESCAPE):
				self.running=False
				return ""
			if ngk.key_pressed(pygame.K_RETURN) and self.cursor>-1:
				self.play_enter_sound()
				self.running=False
				return self.items[self.cursor].reference
			if ngk.key_down(pygame.K_PAGEUP) and self.musictimer.elapsed>=40 and self.music_added==True:
				self.musictimer.restart()
				self.music.volume+=1
			if ngk.key_down(pygame.K_PAGEDOWN) and self.musictimer.elapsed>=40 and self.music_added==True:
				self.musictimer.restart()
				self.music.volume-=1
	def fade_music(self,fadespeed=20):
		fadetimer=ngk.Timer()
		while self.music.volume>-60:
			ngk.process()
			pygame.time.wait(5)
			if fadetimer.elapsed>=fadespeed:
				fadetimer.restart()
				self.music.volume-=1
			if self.music.volume<=-60:
				self.music.stop()