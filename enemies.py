import ngk
from player import player
from random import randint, choice, random
from data import ENEMY_DATA, WEAPON_DATA, ITEM_DATA
import inv

# This list will hold all active enemy instances
enemies = []
cp = ngk.snd.SoundPool()

class Enemy:
    def __init__(self, x, y, enemy_type):
        if enemy_type not in ENEMY_DATA:
            raise ValueError(f"Enemy type '{enemy_type}' not found in ENEMY_DATA.")
        
        data = ENEMY_DATA[enemy_type]

        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        
        self.health = randint(*data["health_range"]) * player.level
        self.max_health = self.health

        self.weapon_name = choice(data["weapons"])
        self.fire_time = data["fire_time"]
        self.xp_range = data["xp_range"]
        self.sounds = data["sounds"]
        self.loot_table = data["loot"]
        self.walk_speed_range = data.get("walk_speed", (340, 500))
        self.detection_range = data.get("detection_range", 100)

        # AI and movement
        self.movetimer = ngk.Timer()
        self.movetime = randint(340, 500)
        self.attacktimer = ngk.Timer()
        self.dir = choice(["left", "right"])
        self.falltime = 1000
        self.is_reloading = False
        self.reload_timer = ngk.Timer()
        weapon_data = WEAPON_DATA.get(self.weapon_name)
        if weapon_data and not weapon_data.get('melee', True):
            self.max_clip_ammo = weapon_data['max_ammo']
            self.clip_ammo = self.max_clip_ammo
        else:
            self.max_clip_ammo = 0
            self.clip_ammo = 0

        self.voicetimer = ngk.Timer()
        self.voicetime = randint(4000, 9000)

        self.usable_items = data.get("usable_items", {})
        self.item_cooldown_timer = ngk.Timer()
        self.item_cooldown_time = randint(8000, 15000)
        self.inventory = {}

        # Check if the weapon exists before trying to play its draw sound
        if self.weapon_name in WEAPON_DATA:
            cp.play_2d(f"{self.weapon_name}draw.ogg", player.x, player.y, self.x, self.y, False)

    def get_random_hit_sound(self):
        """Safely gets a random hit sound from the enemy's sound list."""
        hit_sounds = self.sounds.get("hit_sounds", [])
        if hit_sounds:
            return choice(hit_sounds)
        return ""

def enemy_loop():
    from map import current_map
    from world_objects import spawned_items
    for i in range(len(enemies) - 1, -1, -1):
        enemy = enemies[i]
        
        # If the enemy is in the middle of reloading, check if it's done.
        if enemy.is_reloading:
            weapon_data = WEAPON_DATA.get(enemy.weapon_name)
            if weapon_data and enemy.reload_timer.elapsed >= weapon_data['reload_time']:
                enemy.is_reloading = False
                enemy.clip_ammo = enemy.max_clip_ammo
                reload_sound = weapon_data.get('sounds', {}).get('reload')
                if reload_sound:
                    cp.play_2d(reload_sound, player.x, player.y, enemy.x, enemy.y, False)
            # While reloading, the enemy can still move and talk, but cannot attack or use items.

        # Before moving, check if the enemy is standing on a usable item.
        # We loop backwards because we might remove items from the list.
        for item_index in range(len(spawned_items) - 1, -1, -1):
            item = spawned_items[item_index]
            if item.x == enemy.x and item.y == enemy.y:
                if item.item_name in enemy.usable_items:
                    current_amount = enemy.inventory.get(item.item_name, 0)
                    enemy.inventory[item.item_name] = current_amount + 1
                    
                    # Play the item's pickup sound from the enemy's location
                    pickup_sound = ""
                    if item.item_name in ITEM_DATA:
                        pickup_sound = ITEM_DATA[item.item_name].get('pickup_sound', '')
                    if pickup_sound:
                        cp.play_2d(pickup_sound, player.x, player.y, enemy.x, enemy.y, False)
                    spawned_items.pop(item_index)
                    # An enemy only picks up one item per turn
                    break 
        
        distance_x = abs(player.x - enemy.x)
        is_player_detected = distance_x <= enemy.detection_range

        # Movement AI
        if enemy.movetimer.elapsed >= enemy.movetime:
            enemy.movetimer.restart()
            enemy.movetime = randint(*enemy.walk_speed_range)
            
            moved = False
            if is_player_detected and enemy.weapon_name != "":
                # Combat movement: move towards player
                if enemy.x < player.x:
                    enemy.dir = "right"; enemy.x += 1
                elif enemy.x > player.x:
                    enemy.dir = "left"; enemy.x -= 1
                moved = True
            else:
                # Idle movement: wander randomly
                if randint(1, 3) == 1: # 1 in 3 chance to move when idle
                    if randint(1, 2) == 1: enemy.dir = "right"; enemy.x += 1
                    else: enemy.dir = "left"; enemy.x -= 1
                    moved = True

            if moved:
                walk_sounds = enemy.sounds.get("walk_sounds")
                if walk_sounds:
                    step_sound = choice(walk_sounds)
                else:
                    tile = current_map.get_tile_at(enemy.x, enemy.y)
                    if tile:
                        step_sound = tile + "step" + str(randint(1, 5)) + ".ogg"
                    else:
                        step_sound = ""
                
                if step_sound:
                    cp.play_2d(step_sound, player.x, player.y, enemy.x, enemy.y, False)

        voices = enemy.sounds.get("voices")
        if voices and enemy.voicetimer.elapsed >= enemy.voicetime:
            enemy.voicetimer.restart()
            enemy.voicetime = randint(8000, 20000)
            cp.play_2d(choice(voices), player.x, player.y, enemy.x, enemy.y, False)

        # Check if the enemy is ready to consider using an item.
        if not enemy.is_reloading and enemy.usable_items and enemy.item_cooldown_timer.elapsed >= enemy.item_cooldown_time:
            used_item = False
            for item_name, conditions in enemy.usable_items.items():
                if item_name not in enemy.inventory or enemy.inventory[item_name] <= 0:
                    continue # Skip to the next item if they don't have this one.

                if random() > conditions.get('chance', 1.0):
                    continue # Failed the chance roll for this item

                # Health Drink Logic ---
                if item_name == 'health drink':
                    health_threshold = conditions.get('health_threshold', 0.3)
                    if (enemy.health / enemy.max_health) <= health_threshold:
                        item_data = ITEM_DATA.get(item_name)
                        if item_data:
                            heal_amount = randint(*item_data['value_range'])
                            enemy.health = min(enemy.max_health, enemy.health + heal_amount)
                            if item_data.get('sound'):
                                cp.play_2d(item_data['sound'], player.x, player.y, enemy.x, enemy.y, False)
                            used_item = True
                        enemy.inventory[item_name] -= 1
                        break # Use only one item per cycle

                # Guided Missile Logic ---
                elif item_name == 'guided missile':
                    item_data = ITEM_DATA.get(item_name)
                    if item_data:
                        possible_targets = [p for p in enemies if p != enemy]
                        possible_targets.append(player) # Player is a valid target object here
                        
                        if possible_targets:
                            target = choice(possible_targets)
                            # The spawn_guided_missile function needs a "launcher" context, which is the player.
                            # For enemies, we can temporarily set the player's position to the enemy's
                            # for the spawn call to ensure the missile originates from the correct place.
                            original_player_pos = (player.x, player.y)
                            player.x, player.y = enemy.x, enemy.y
                            from world_objects import spawn_guided_missile
                            # We create a fake 'player' context for spawning, as the missile function expects it
                            # The target, however, is the randomly chosen one.
                            spawn_guided_missile(target, item_data)
                            player.x, player.y = original_player_pos
                            used_item = True
                        enemy.inventory[item_name] -= 1
                    break

                elif ITEM_DATA.get(item_name, {}).get('type') == 'explosive':
                    # For explosives, the main condition is simply the 'chance' roll we already did.
                    # We just need to spawn it at the enemy's location.
                    item_data = ITEM_DATA.get(item_name)
                    if item_data:
                        from world_objects import spawn_explosive
                        # The spawn_explosive function also uses the player's position for sound.
                        # We'll use the same temporary position swap trick.
                        original_player_pos = (player.x, player.y)
                        player.x, player.y = enemy.x, enemy.y
                        spawn_explosive(enemy.x, enemy.y, item_data)
                        player.x, player.y = original_player_pos
                        used_item = True
                        enemy.inventory[item_name] -= 1
                    break

                elif ITEM_DATA.get(item_name, {}).get('type') == 'interceptor':
                    item_data = ITEM_DATA.get(item_name)
                    if item_data:
                        from world_objects import spawn_interceptor_field
                        original_player_pos = (player.x, player.y)
                        player.x, player.y = enemy.x, enemy.y
                        spawn_interceptor_field(item_data)
                        player.x, player.y = original_player_pos
                        used_item = True
                        enemy.inventory[item_name] -= 1
                    break
                            
            # If any item was used, reset the cooldown timer
            if used_item:
                enemy.item_cooldown_timer.restart()
                enemy.item_cooldown_time = randint(10000, 20000)

        # attack AI
        weapon_data = WEAPON_DATA.get(enemy.weapon_name)
        if not enemy.is_reloading and is_player_detected and weapon_data and enemy.attacktimer.elapsed >= enemy.fire_time:
            weapon_range = weapon_data["range"]

            if distance_x <= weapon_range:
                # Check for ammo before firing
                if enemy.clip_ammo > 0:
                    enemy.attacktimer.restart()
                    enemy.clip_ammo -= 1
                    
                    damage = randint(*weapon_data["damage_range"])
                    speed = weapon_data["speed"]
                    is_melee = weapon_data["melee"]

                    from projectiles import spawn_ebullet
                    spawn_ebullet(enemy.x, enemy.y, damage, weapon_range, speed, enemy.weapon_name, is_melee, enemy.dir, enemy)
                
                # Out of ammo: start reloading
                else:
                    enemy.is_reloading = True
                    enemy.reload_timer.restart()
                    empty_sound = weapon_data.get('sounds', {}).get('empty')
                    if empty_sound:
                        cp.play_2d(empty_sound, player.x, player.y, enemy.x, enemy.y, False)

        if enemy.health <= 0:
            from world_objects import spawn_bodyfall
            death_sound = enemy.sounds.get("death", "")
            if death_sound:
                cp.play_2d(death_sound, player.x, player.y, enemy.x, enemy.y, False)
            
            player.xp += randint(*enemy.xp_range)
            spawn_bodyfall(enemy.x, enemy.y, enemy.falltime)
            
            for item, loot_info in enemy.loot_table.items():
                if random() <= loot_info["chance"]:
                    amount = randint(*loot_info["amount_range"])
                    if item == "coin":
                        from world_objects import spawn_coin
                        spawn_coin(enemy.x, enemy.y)
                    else:
                        inv.give(item, amount)
                        ngk.speak(f"Picked up {amount} {item}")
            
            enemies.pop(i)

def spawn_enemy(x, y, enemy_type):
    enemies.append(Enemy(x, y, enemy_type))

def kill_enemies():
    enemies.clear()
