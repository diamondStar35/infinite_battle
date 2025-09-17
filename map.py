import json
import os
import ngk
from random import randint, choice
from world_objects import spawn_source, spawn_tree, spawn_metal
from enemies import spawn_enemy

class Map:
    def __init__(self):
        self.name = ""
        self.maxx = 0
        self.maxy = 0
        self.required_level = 1
        self.tiles = {}
        self.properties = {}
        self.objects = []

    def load(self, map_name):
        """Loads and parses a map file from the maps directory."""
        self.reset()
        map_path = os.path.join("maps", f"{map_name}.json")
        try:
            with open(map_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Map file not found at {map_path}")
            return False

        self.properties = data.get("properties", {})
        self.name = self.properties.get("name", "Unnamed Map")
        self.maxx = self.properties.get("maxx", 100)
        self.maxy = self.properties.get("maxy", 100)
        self.required_level = self.properties.get("required_level", 1)
        
        tile_data = data.get("tiles", [])
        for tile_region in tile_data:
            for x in range(tile_region["x1"], tile_region["x2"] + 1):
                self.tiles[f"{x} {tile_region['y']}"] = tile_region["type"]
        
        self.objects = data.get("objects", [])
        return True

    def build_world(self):
        """Spawns all objects defined in the map file."""
        from player import player
        from datetime import datetime
        
        # 1. Set ambient sounds based on properties and time
        current_hour = datetime.now().hour
        ambient_sound = self.properties.get("ambient_night")
        if 3 < current_hour < 20:
            ambient_sound = self.properties.get("ambient_day", ambient_sound)
        
        if ambient_sound:
            spawn_source(0, self.maxx, 0, self.maxy, ambient_sound)

        # 2. Spawn all other objects
        for obj in self.objects:
            obj_type = obj.get("type")
            
            if obj_type == "source":
                spawn_source(obj["x1"], obj["x2"], obj["y1"], obj["y2"], obj["file"])
            
            elif obj_type == "tree_zone":
                for _ in range(obj.get("count", 1)):
                    x = randint(obj["x1"], obj["x2"])
                    spawn_tree(x, obj["y"])
            
            elif obj_type == "enemy_spawn_zone":
                 pass
            
            elif obj_type == "metal":
                spawn_metal(obj["x"], obj["y"])
    
    def get_tile_at(self, x, y):
        return self.tiles.get(f"{x} {y}", "")

    def reset(self):
        """Clears all map data."""
        self.__init__()

current_map = Map()
