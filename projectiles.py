import ngk
from player import player
from random import randint
from enemies import enemies
from weapons import Weapon

bullets = []
ebullets = []
cp = ngk.snd.SoundPool()

#  Player Projectiles ---
class Bullet:
    def __init__(self, x, y, damage, range, speed, name):
        self.x = x
        self.y = y
        self.wname = name
        self.dir = player.facing
        self.damage = damage
        self.range = range
        self.speed = speed
        self.movetimer = ngk.Timer()
        fire_sound = player.weapon.get_sound("fire")
        if fire_sound:
            self.bsound = cp.play_stationary(fire_sound, False)
        self.distance = 0

def bullet_loop():
    from map import current_map
    for i in range(len(bullets) - 1, -1, -1):
        bullet = bullets[i]
        cp.update_listener_2d(player.x, player.y)
        
        if bullet.movetimer.elapsed >= bullet.speed:
            bullet.movetimer.restart()
            if bullet.dir == "right": bullet.x += 1
            else: bullet.x -= 1
            bullet.distance += 1

        # Check for collision with enemies
        for enemy in enemies:
            if bullet.x == enemy.x and bullet.y == enemy.y:
                hit_sound = player.weapon.get_random_hit_sound() # Use new method
                if hit_sound:
                    cp.play_2d(f"{hit_sound}{randint(1,3)}.ogg", player.x, player.y, enemy.x, enemy.y, False)
                enemy_hit_sound = enemy.get_random_hit_sound()
                if enemy_hit_sound:
                    cp.play_2d(enemy_hit_sound, player.x, player.y, enemy.x, enemy.y, False)
                
                enemy.health -= bullet.damage
                bullets.pop(i)
                return # Exit loop for this frame as bullet is gone

        if bullet.distance > bullet.range or bullet.x == 0 or bullet.x == current_map.maxx:
            bullets.pop(i)

def spawn_bullet(x, y, damage, range, speed, name):
    bullets.append(Bullet(x, y, damage, range, speed, name))

def kill_bullets():
    bullets.clear()

#  Enemy Projectiles ---
class EBullet:
    def __init__(self, x, y, damage, range, speed, name, is_melee, direction, launcher):
        self.x = x
        self.y = y
        self.wname = name
        self.dir = direction
        self.launcher = launcher
        self.damage = damage
        self.range = range
        self.speed = speed
        self.movetimer = ngk.Timer()
        self.is_melee = is_melee
        self.weaponsound = cp.play_2d(f"{self.wname}.ogg", player.x, player.y, x, y, False)
        self.distance = 0

def ebullet_loop():
    from map import current_map
    for i in range(len(ebullets) - 1, -1, -1):
        ebullet = ebullets[i]
        if not ebullet.is_melee:
            cp.update_listener_2d(player.x, player.y)
            cp.update_sound_2d(ebullet.weaponsound, ebullet.x, ebullet.y)
            
        if ebullet.movetimer.elapsed >= ebullet.speed:
            ebullet.movetimer.restart()
            if ebullet.dir == "right": ebullet.x += 1
            else: ebullet.x -= 1
            ebullet.distance += 1

        # Check for collision with player
        if ebullet.x == player.x and ebullet.y == player.y:
            weapon_obj = Weapon(ebullet.wname)
            hit_sound = weapon_obj.get_random_hit_sound()
            if hit_sound:
                cp.play_stationary(hit_sound, False)

            player.health -= ebullet.damage
            ebullets.pop(i)
            return

        # Check for collision with player bullets (parry)
        for j in range(len(bullets) - 1, -1, -1):
            pbullet = bullets[j]
            if ebullet.x == pbullet.x and ebullet.y == pbullet.y and "sword" in pbullet.wname and "sword" in ebullet.wname:
                cp.play_2d(f"{ebullet.wname}block.ogg", player.x, player.y, ebullet.x, ebullet.y, False)
                if randint(1, 2) == 2:
                    cp.play_2d(f"{ebullet.wname}drop.ogg", player.x, player.y, ebullet.launcher.x, ebullet.launcher.y, False)
                    ngk.speak("Enemy disarmed.")
                    ebullet.launcher.weapon_name = ""
                ebullets.pop(i)
                bullets.pop(j)
                return # Both projectiles are gone

        if ebullet.distance > ebullet.range or ebullet.x == 0 or ebullet.x == current_map.maxx:
            if not ebullet.is_melee:
                cp.play_2d(f"{ebullet.wname}shell{randint(1,3)}.ogg", player.x, player.y, ebullet.x, ebullet.y, False)
            ebullets.pop(i)

def spawn_ebullet(x, y, damage, range, speed, name, is_melee, direction, launcher):
    ebullets.append(EBullet(x, y, damage, range, speed, name, is_melee, direction, launcher))

def kill_ebullets():
    ebullets.clear()
