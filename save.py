from player import player
import sd

key="get_your_big_fat_ugly_stupid_ass_out_of_here!"
data=sd.savedata("data.dat",key)

def loaddata():
	data.load()
	if data.exists("health"): player.health=data.get("health")
	if data.exists("inv"): player.inv=data.get("inv")
	if data.exists("ammo1"): player.ammo1=data.get("ammo1")
	if data.exists("xp"): player.xp=data.get("xp")
	if data.exists("xprequired"): player.xprequired=data.get("xprequired")
	if data.exists("level"): player.level = data.get("level")
	if data.exists("firstplayed"): player.firstplayed=data.get("firstplayed")
	if data.exists("mapsunlocked"): player.mapsunlocked=data.get("mapsunlocked")
	if data.exists("resurrections"): player.resurrections=data.get("resurrections")
	player.update_max_health()

def writedata():
	data.add("health",player.health)
	data.add("inv",player.inv)
	data.add("ammo1",player.ammo1)
	data.add("xp",player.xp)
	data.add("xprequired",player.xprequired)
	data.add("level", player.level)
	data.add("firstplayed",player.firstplayed)
	data.add("mapsunlocked",player.mapsunlocked)
	data.add("resurrections", player.resurrections)
	data.save()
