import ngk
from player import player
from random import randint, choice
from projectiles import bullets, ebullets
from enemies import enemies
from data import ITEM_DATA, AMMO_DATA
import inv

cp = ngk.snd.SoundPool()
trees, sources, staircases, coins, bodyfalls, cans, metals, explosives, spawned_items, guided_missiles, interceptor_fields = [], [], [], [], [], [], [], [], [], [], []

class Tree:
    def __init__(self, tx, ty):
        self.x, self.y = tx, ty
        self.hp = randint(10, 30)
        from map import current_map
        self.oldplat = current_map.get_tile_at(tx, ty)
        self.sc = spawn_staircase(tx, tx, ty, ty + (self.hp - 4), "tree")

def tree_loop():
    for i in range(len(trees) - 1, -1, -1):
        tree = trees[i]
        for bullet in bullets:
            if bullet.x == tree.x and player.weapon.name == "axe":
                cp.play_2d(f"treehit{randint(1,3)}.ogg", player.x, player.y, tree.x, tree.y, False)
                tree.hp -= bullet.damage
                bullets.remove(bullet)
                return
        if tree.hp <= 0:
            cp.play_2d("treefall.ogg", player.x, player.y, tree.x, tree.y, False)
            tree.sc.kill()
            from game import spawn_platform
            spawn_platform(tree.x, tree.x, tree.y, tree.oldplat)
            staircases.remove(tree.sc)
            trees.pop(i)

def spawn_tree(tx, ty):
    trees.append(Tree(tx, ty))

class Source:
    def __init__(self, sx1, sx2, sy1, sy2, sf):
        self.x1, self.x2, self.y1, self.y2 = sx1, sx2, sy1, sy2
        self.file = sf
        self.sound = cp.play_2d(self.file, player.x, player.y, self.x1, self.y1, True)

def source_loop():
    for src in sources:
        cp.update_listener_2d(player.x, player.y)
        cp.update_sound_range_2d(src.sound, (player.x - src.x1), (src.x2 - src.x1), (player.y - src.y1), (src.y2 - src.y1), True)

def spawn_source(sx1, sx2, sy1, sy2, sf):
    sources.append(Source(sx1, sx2, sy1, sy2, sf))

def kill_sources():
    for src in sources:
        cp.destroy_sound(src.sound)
    sources.clear()

class Staircase:
    def __init__(self, mx, mx2, my, my2, type):
        self.minx, self.maxx, self.miny, self.maxy = mx, mx2, my, my2
        self.abletojump = True
        self.plattype = type
        from game import spawn_platform
        for i in range(my, my2 + 1):
            spawn_platform(mx, mx2, i, type)

    def kill(self):
        from game import spawn_platform
        for i in range(self.miny, self.maxy + 1):
            spawn_platform(self.minx, self.maxx, i + 1, "")

def staircase_loop():
    on_any_staircase = False
    for i in staircases:
        if player.x >= i.minx and player.x <= i.maxx and player.y >= i.miny and player.y <= i.maxy:
            on_any_staircase = True
            player.onstaircase = True
            i.abletojump = (player.y == i.maxy)
            if ngk.key_down(ngk.K_UP) and player.movetimer.elapsed >= player.movetime and player.y < i.maxy:
                player.movetimer.restart()
                if not player.jumping: cp.play_stationary(f"{i.plattype}step{randint(1,5)}.ogg", False)
                player.y += 1
            if ngk.key_down(ngk.K_DOWN) and player.movetimer.elapsed >= player.movetime and player.y > i.miny:
                player.movetimer.restart()
                if not player.jumping: cp.play_stationary(f"{i.plattype}step{randint(1,5)}.ogg", False)
                player.y -= 1
    if not on_any_staircase:
        player.onstaircase = False

def spawn_staircase(mx, mx2, my, my2, type):
    sc1 = Staircase(mx, mx2, my, my2, type)
    staircases.append(sc1)
    return sc1

class Coin:
    def __init__(self, cx, cy):
        self.x, self.y = cx, cy
        self.beeptimer = ngk.Timer()
        self.beeptime = randint(250, 400)
        self.amount = randint(3, 20)
        self.existtimer = ngk.Timer()
        self.existtime = randint(30000, 60000)

def coin_loop():
    for i in range(len(coins) - 1, -1, -1):
        coin = coins[i]
        if coin.existtimer.elapsed >= coin.existtime:
            coins.pop(i)
            continue
        if coin.beeptimer.elapsed >= coin.beeptime:
            coin.beeptimer.restart()
            cp.play_2d("gold.ogg", player.x, player.y, coin.x, coin.y, False)
        if player.x == coin.x and player.y == coin.y:
            cp.play_stationary("goldpickup.ogg", False)
            player.gold += coin.amount
            ngk.speak(f"Got {coin.amount} gold")
            coins.pop(i)

def spawn_coin(cx, cy):
    coins.append(Coin(cx, cy))

class Bodyfall:
    def __init__(self, bx, by, btime):
        self.x, self.y, self.falltime = bx, by, btime
        from map import current_map
        self.tile = current_map.get_tile_at(bx, by)
        self.falltimer = ngk.Timer()

def bodyfall_loop():
    for i in range(len(bodyfalls) - 1, -1, -1):
        bf = bodyfalls[i]
        if bf.falltimer.elapsed >= bf.falltime:
            cp.play_2d(f"{bf.tile}hardland.ogg", player.x, player.y, bf.x, bf.y, False)
            bodyfalls.pop(i)

def spawn_bodyfall(bx, by, btime):
    bodyfalls.append(Bodyfall(bx, by, btime))

class Can:
    def __init__(self, cx, cy):
        self.x, self.y = cx, cy
        self.range, self.movetime, self.dist = 5, 60, 0
        self.movetimer = ngk.Timer()
        self.dir = player.facing
        cp.play_2d("canthrow.ogg", player.x, player.y, self.x, self.y, False)

def can_loop():
    from map import current_map
    for i in range(len(cans) - 1, -1, -1):
        can = cans[i]
        if can.movetimer.elapsed >= can.movetime:
            can.movetimer.restart()
            if can.dir == "left": can.x -= 1
            else: can.x += 1
            can.dist += 1
        if can.dist > can.range or can.x == 0 or can.x == current_map.maxx:
            cp.play_2d("candrop.ogg", player.x, player.y, can.x, can.y, False)
            cans.pop(i)

def spawn_can(cx, cy):
    cans.append(Can(cx, cy))

class Metal:
    def __init__(self, mx, my):
        self.x = mx
        self.y = my
        from map import current_map
        self.oldplat = current_map.get_tile_at(mx, my)
        from game import spawn_platform
        spawn_platform(mx, mx, my, "metal")

def metalloop():
    for i in range(len(metals) - 1, -1, -1):
        metal = metals[i]
        for i2 in range(len(bullets) - 1, -1, -1):
            bullet = bullets[i2]
            if bullet.x == metal.x and bullet.y == metal.y:
                ngk.speak("A manhole is gone.")
                from game import spawn_platform
                spawn_platform(metal.x, metal.x, metal.y, metal.oldplat)
                bullets.pop(i2)
                metals.pop(i)
                return

def spawn_metal(mx, my):
    metals.append(Metal(mx, my))

class Explosive:
    def __init__(self, ex, ey, item_data):
        self.x, self.y = ex, ey
        
        self.detonation_time = item_data.get("detonation_time", 3000)
        self.blast_radius = item_data.get("blast_radius", 5)
        self.damage_range = item_data.get("damage_range", (10, 20))
        self.damage_falloff = item_data.get("damage_falloff", True)
        self.sounds = item_data.get("sounds", {})
        
        self.detonation_timer = ngk.Timer()
        self.fuse_sound = None

        throw_sound = self.sounds.get("throw")
        if throw_sound:
            cp.play_2d(throw_sound, player.x, player.y, self.x, self.y, False)
        
        fuse_sound_file = self.sounds.get("fuse")
        if fuse_sound_file:
            self.fuse_sound = cp.play_2d(fuse_sound_file, player.x, player.y, self.x, self.y, True)

def explosive_loop():
    for i in range(len(explosives) - 1, -1, -1):
        explosive = explosives[i]

        if explosive.fuse_sound:
            cp.update_sound_2d(explosive.fuse_sound, explosive.x, explosive.y)

        if explosive.detonation_timer.elapsed >= explosive.detonation_time:
            if explosive.fuse_sound:
                cp.destroy_sound(explosive.fuse_sound)

            explode_sound = explosive.sounds.get("explode")
            if explode_sound:
                cp.play_2d(explode_sound, player.x, player.y, explosive.x, explosive.y, False)

            # Check player
            player_dist = abs(player.x - explosive.x)
            if player_dist <= explosive.blast_radius:
                damage = calculate_damage(explosive, player_dist)
                player.health -= damage
                ngk.speak(f"You took {damage} blast damage.")
            
            # Check enemies
            for enemy in enemies:
                enemy_dist = abs(enemy.x - explosive.x)
                if enemy_dist <= explosive.blast_radius:
                    damage = calculate_damage(explosive, enemy_dist)
                    enemy.health -= damage
            explosives.pop(i)

def calculate_damage(explosive, distance):
    """Calculates damage, applying falloff if enabled."""
    base_damage = randint(*explosive.damage_range)
    if not explosive.damage_falloff or explosive.blast_radius == 0:
        return base_damage
    
    # Linear damage falloff: damage is 100% at distance 0, and 0% at max radius
    falloff_multiplier = 1 - (distance / explosive.blast_radius)
    final_damage = int(base_damage * falloff_multiplier)
    return max(1, final_damage)

def spawn_explosive(ex, ey, item_data):
    explosives.append(Explosive(ex, ey, item_data))

class SpawnedItem:
    def __init__(self, sx, sy, item_name):
        self.x, self.y = sx, sy
        self.item_name = item_name
        self.exist_timer = ngk.Timer()
        self.exist_time = 90000
        self.proximity_alert_timer = ngk.Timer()
        self.proximity_alert_cooldown = 500

def spawned_item_loop():
    for i in range(len(spawned_items) - 1, -1, -1):
        item = spawned_items[i]

        # 1. Check for expiration
        if item.exist_timer.elapsed >= item.exist_time:
            spawned_items.pop(i)
            continue

        # 2. Check for player pickup
        if player.x == item.x and player.y == item.y:
            pickup_sound = ""
            if item.item_name in AMMO_DATA:
                amount = randint(50, 100)
                inv.give(item.item_name, amount)
                pickup_sound = AMMO_DATA[item.item_name].get('pickup_sound', '')
                ngk.speak(f"Picked up an ammo pack, containing {amount} {item.item_name}.")
            # Handle regular items
            elif item.item_name in ITEM_DATA:
                inv.give(item.item_name, 1)
                pickup_sound = ITEM_DATA[item.item_name].get('pickup_sound', '')
                ngk.speak(f"Picked up {item.item_name}.")

            if pickup_sound:
                cp.play_stationary(pickup_sound, False)
            
            spawned_items.pop(i)
            continue

        # 3. Check for proximity alert
        distance = abs(player.x - item.x)
        if distance <= 10 and item.proximity_alert_timer.elapsed >= item.proximity_alert_cooldown:
            item.proximity_alert_timer.restart()
            cp.play_2d("item_proximity_chime.ogg", player.x, player.y, item.x, item.y, False)

def spawn_random_item():
    from map import current_map
    
    possible_items = list(ITEM_DATA.keys()) + list(AMMO_DATA.keys())
    if not possible_items:
        return # No items to spawn

    item_to_spawn = choice(possible_items)    
    # Spawn on the ground floor (y=0) at a random x coordinate
    x = randint(0, current_map.maxx)
    y = 0

    spawned_items.append(SpawnedItem(x, y, item_to_spawn))

class GuidedMissile:
    def __init__(self, target, item_data):
        self.x, self.y = player.x, player.y
        self.target = target        
        self.speed = item_data.get("speed", 100)
        self.blast_radius = item_data.get("blast_radius", 4)
        self.damage_range = item_data.get("damage_range", (50, 75))
        self.sounds = item_data.get("sounds", {})
        
        self.movetimer = ngk.Timer()
        self.travel_sound = None
        self.warning_sound_cooldown = ngk.Timer()

        cp.play_stationary(self.sounds.get("launch", ""), False)
        travel_sound_file = self.sounds.get("travel", "")
        if travel_sound_file:
            self.travel_sound = cp.play_2d(travel_sound_file, player.x, player.y, self.x, self.y, True)

    def update(self):
        if self.target not in enemies:
            self.explode()
            return

        # Movement logic
        if self.movetimer.elapsed >= self.speed:
            self.movetimer.restart()
            if self.x < self.target.x: self.x += 1
            elif self.x > self.target.x: self.x -= 1
        
        # Update sound positions
        if self.travel_sound:
            cp.update_sound_2d(self.travel_sound, self.x, self.y)

        # Play warning sound if near player
        player_dist = abs(player.x - self.x)
        if player_dist <= 15 and self.warning_sound_cooldown.elapsed >= 1000:
            self.warning_sound_cooldown.restart()
            cp.play_2d(self.sounds.get("warning", ""), player.x, player.y, self.x, self.y, False)

        # Check for impact
        if self.x == self.target.x and self.y == self.target.y:
            self.explode()
            
    def explode(self):
        if self.travel_sound:
            cp.destroy_sound(self.travel_sound)
        
        cp.play_2d(self.sounds.get("explode", ""), player.x, player.y, self.x, self.y, False)

        # Apply AoE damage
        # Check player
        if abs(player.x - self.x) <= self.blast_radius:
            player.health -= randint(*self.damage_range) # Missiles do full damage in radius
        
        # Check enemies
        for enemy in enemies:
            if abs(enemy.x - self.x) <= self.blast_radius:
                enemy.health -= randint(*self.damage_range)
        
        # Mark for removal
        if self in guided_missiles:
            guided_missiles.remove(self)

def guided_missile_loop():
    for i in range(len(guided_missiles) - 1, -1, -1):
        missile = guided_missiles[i]
        missile.update()

def spawn_guided_missile(target, item_data):
    guided_missiles.append(GuidedMissile(target, item_data))

class InterceptorField:
    def __init__(self, item_data):
        self.x, self.y = player.x, player.y
        self.range = item_data.get("range", 10)
        self.duration = item_data.get("duration", 3000)
        self.sounds = item_data.get("sounds", {})
        self.duration_timer = ngk.Timer()
        cp.play_stationary(self.sounds.get("activate", ""), False)

def interceptor_loop():
    for i in range(len(interceptor_fields) - 1, -1, -1):
        field = interceptor_fields[i]
        
        # Check for expiration
        if field.duration_timer.elapsed >= field.duration:
            interceptor_fields.pop(i)
            continue
        
        # Check for nearby missiles
        for j in range(len(guided_missiles) - 1, -1, -1):
            missile = guided_missiles[j]
            if abs(missile.x - field.x) <= field.range:
                # Intercept!
                cp.play_2d(field.sounds.get("intercept", ""), player.x, player.y, missile.x, missile.y, False)
                if missile.travel_sound:
                    cp.destroy_sound(missile.travel_sound)
                guided_missiles.pop(j)
                interceptor_fields.pop(i) # Field is consumed on use
                break

def spawn_interceptor_field(item_data):
    if not interceptor_fields:
        interceptor_fields.append(InterceptorField(item_data))

def clear_all_world_objects():
    trees.clear()
    sources.clear()
    staircases.clear()
    coins.clear()
    bodyfalls.clear()
    cans.clear()
    metals.clear()
    explosives.clear()
    spawned_items.clear()
    guided_missiles.clear()
    interceptor_fields.clear()
