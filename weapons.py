from data import WEAPON_DATA
from random import choice

class Weapon:
    def __init__(self, name):
        data = WEAPON_DATA.get(name)
        if not data:
            raise ValueError(f"Weapon '{name}' not found in WEAPON_DATA.")

        self.name = name
        self.damage_range = data["damage_range"]
        self.range = data["range"]
        self.fire_time = data["fire_time"]
        self.speed = data["speed"]
        self.is_melee = data["melee"]
        self.is_auto = data["auto"]
        self.reload_time = data["reload_time"]
        self.max_ammo = data["max_ammo"]
        self.sounds = data["sounds"]

    def get_sound(self, sound_type):
        """Safely gets a sound file name for a specific action."""
        return self.sounds.get(sound_type, "")

    def get_random_hit_sound(self):
        """Safely gets a random hit sound from the weapon's sound list."""
        hit_sounds = self.sounds.get("hit_sounds", [])
        if hit_sounds:
            return choice(hit_sounds)
        return ""
