import ngk
from random import randint
from weapons import Weapon
from data import WEAPON_DATA


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.facing = "right"
        self.base_health = 10000
        self.max_health = self.base_health
        self.health = self.base_health # Current health
        self.resurrection_health_multiplier = 1.00
        self.gold = 500
        self.firstplayed = True
        self.mapsunlocked = ["forest"]

        # Movement & State
        self.movetimer = ngk.Timer()
        self.movetime = 0
        self.walktime = 240
        self.runtime = 190
        self.jumping = False
        self.falling = False
        self.rising = False
        self.lowering = False
        self.onstaircase = False
        self.canjump = 0

        # Jumping/Falling Attributes
        self.jumptimer = ngk.Timer()
        self.jumptime = 140
        self.jumpcounter = 0
        self.jumpheight = 5
        self.falltimer = ngk.Timer()
        self.falltime = 110
        self.fallcounter = 0

        # Combat & Weapon Attributes
        self.weapontimer = ngk.Timer()
        self.reloadtimer = ngk.Timer()
        self.weapon = Weapon("unarmed") # Player holds a weapon object
        self.reloading = False
        self.weaponjams = 0
        self.swordsharpness = 5
        self.resurrections = 0

        # Inventory
        self.inv = {}
        self.invpos = 0
        self.invitem = ""
        self.slots = ["", "", "", "", ""]
        self.ammo1 = {}  # In clip

        # XP and Leveling
        self.xp = 0
        self.xprequired = 200
        self.level = 1
        
        # Gathering
        self.gatheredtiles = []
        self.gathertimer = ngk.Timer()
        self.gathertime = 40
        self.gathering = False
        self.gatherprogress = 0
        self.gatheramount = 0
        self.haspickaxe = False

        # Misc
        self.currenttime = ""
        self.espawntimer = ngk.Timer()
        self.espawntime = 15000
        self.item_spawn_timer = ngk.Timer()
        self.item_spawn_time = 5000
        self.enemytypes = [1]

    def update_max_health(self):
        """Recalculates max health based on resurrections and heals the player."""
        old_max = self.max_health
        self.max_health = int(self.base_health * (1 + (self.resurrections * self.resurrection_health_multiplier)))
        health_gain = self.max_health - old_max
        if health_gain > 0:
            self.health += health_gain
        # Ensure current health doesn't exceed new max
        if self.health > self.max_health:
            self.health = self.max_health

    def give_item(self, item, amount=1):
        current_amount = self.inv.get(item, 0)
        new_amount = current_amount + amount
        if new_amount <= 0:
            if item in self.inv:
                del self.inv[item]
                # If the removed item was the current one, reset selection
                if self.invitem == item:
                    self.invitem = ""
                    self.invpos = 0
        else:
            self.inv[item] = new_amount

    def get_inventory_keys(self):
        return list(self.inv.keys())

    def cycle_inventory(self, direction):
        keys = self.get_inventory_keys()
        if not keys:
            ngk.speak("No items")
            return

        if direction == 1:  # Forward
            self.invpos += 1
        else:  # Backward
            self.invpos -= 1

        if self.invpos >= len(keys):
            self.invpos = 0
        elif self.invpos < 0:
            self.invpos = len(keys) - 1

        self.invitem = keys[self.invpos]
        item_count = self.inv.get(self.invitem, 0)
        
        # Helper for pluralization
        def plural(num, singular, plural_form):
            return singular if num == 1 else plural_form

        plural_name = plural(item_count, self.invitem, self.invitem + "s")
        ngk.speak(f"{plural_name}, you have {item_count}.")

    def equip_weapon(self, weapon_name):
        """Equips a weapon by creating a new Weapon object."""
        if weapon_name not in WEAPON_DATA:
            return
            
        self.weapon = Weapon(weapon_name)
        
        from game import play
        draw_sound = self.weapon.get_sound("draw")
        if draw_sound:
            play(draw_sound, False)
        ngk.speak(weapon_name if weapon_name != "unarmed" else "Unarmed")

    def reload_weapon(self):
        w = self.weapon
        if w.is_melee:
            ngk.speak("This weapon doesn't use ammo.")
            return

        ammo_type = w.sounds.get("ammo_type")
        if not ammo_type:
            ngk.speak("This weapon has an undefined ammo type.")
            return

        clip_ammo = self.ammo1.get(w.name, 0)        
        if clip_ammo >= w.max_ammo:
            ngk.speak("Clip is full.")
            return

        reserve_ammo = self.inv.get(ammo_type, 0)
        if reserve_ammo <= 0:
            ngk.speak(f"You have no more {ammo_type}.")
            return
        
        from game import play
        self.reloadtimer.restart()
        self.reloading = True
        reload_sound = w.get_sound("reload")
        if reload_sound:
            play(reload_sound, False)

        needed = w.max_ammo - clip_ammo
        transfer = min(needed, reserve_ammo)
        
        self.ammo1[w.name] = clip_ammo + transfer
        self.give_item(ammo_type, -transfer) # Use give_item to remove from inventory

    def get_weapon_names(self):
        return [w for w in WEAPON_DATA.keys() if w != "unarmed"]

# Create a single, globally accessible instance of the Player.
# While not perfect, this is a huge improvement over dozens of global variables.
# Other modules will now do 'from player import player' to access it.
player = Player()
