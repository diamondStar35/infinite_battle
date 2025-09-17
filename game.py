import ngk
import save
import pygame
import sys
from player import player
from random import randint, choice
from datetime import datetime
from map import current_map
import enemies
from enemies import enemies as enemy_list
from data import ITEM_DATA
import projectiles
import world_objects
import inv

p = ngk.snd.SoundPool()

def game():
    p.play_stationary("spawn.ogg", False)
    if player.firstplayed:
        inv.give("revolver", 1)
        player.ammo1["revolver"] = 6
        inv.give("revolver cartridges", 500)
        player.firstplayed = False
        save.writedata()
        
    while True:
        projectiles.bullet_loop()
        projectiles.ebullet_loop()
        enemies.enemy_loop()
        world_objects.staircase_loop()
        world_objects.coin_loop()
        world_objects.can_loop()
        world_objects.bodyfall_loop()
        world_objects.tree_loop()
        world_objects.source_loop()
        world_objects.metalloop()
        world_objects.explosive_loop()
        world_objects.spawned_item_loop()
        world_objects.guided_missile_loop()
        world_objects.interceptor_loop()

        p.update_listener_2d(player.x, player.y)
        ngk.process()
        pygame.time.wait(5)
        
        if player.jumping: player.movetime = player.jumptime
        elif altisdown(): player.movetime = player.runtime
        else: player.movetime = player.walktime
            
        # Player Input ---
        if ngk.key_pressed(ngk.K_TAB): inv.cycle_inv(1 if not shiftisdown() else 0)
        if ngk.key_pressed(ngk.K_RETURN): inv.useitem()
        
        if ngk.key_pressed(ngk.K_t):
            if not player.haspickaxe: pass
            elif (player.x, player.y) in player.gatheredtiles: ngk.speak("You already gathered there.")
            elif gmt() not in ["stone", "metal"]: pass
            else:
                if gmt() == "stone": player.gatheramount = randint(20, 35)
                elif gmt() == "metal": player.gatheramount = randint(40, 60)
                if not player.gathering:
                    ngk.speak("Gathering started")
                    player.gathering = True

        if ngk.key_pressed(ngk.K_h): ngk.speak(f"{player.health} of {player.max_health} health")
        if ngk.key_pressed(ngk.K_m): ngk.speak(f"{player.gold} gold")
        if ngk.key_pressed(ngk.K_c): ngk.speak(f"{player.x}, {player.y}")
        if ngk.key_pressed(ngk.K_l): 
            ngk.speak(f"Level {player.level}, with {player.xp} XP. You  need {player.xprequired - player.xp} to the next level. Resurrection {player.resurrections}.")

        if ngk.key_pressed(ngk.K_n):
            nearest_enemy = None
            min_distance = 101

            for enemy in enemies.enemies:
                distance = abs(player.x - enemy.x)
                if distance <= 100 and distance < min_distance:
                    min_distance = distance
                    nearest_enemy = enemy
            
            if nearest_enemy:
                direction = "right" if nearest_enemy.x > player.x else "left"
                enemy_name = nearest_enemy.enemy_type.replace('_', ' ')
                ngk.speak(f"Nearest enemy: a {enemy_name} is {min_distance} tiles to your {direction}.")
            else:
                ngk.speak("No enemies detected nearby.")

        if ngk.key_down(pygame.K_LEFT) and player.movetimer.elapsed >= player.movetime and player.x > 0 and not player.gathering:
            player.movetimer.restart(); player.facing = "left"; player.x -= 1; playstep()
        if ngk.key_down(pygame.K_RIGHT) and player.movetimer.elapsed >= player.movetime and player.x < current_map.maxx and not player.gathering:
            player.movetimer.restart(); player.facing = "right"; player.x += 1; playstep()

        if ngk.key_pressed(pygame.K_SPACE) and not any([player.jumping, player.falling, player.rising, player.lowering, player.gathering]):
            play("jump.ogg", False); player.jumping = True; player.rising = True

        if ngk.key_pressed(ngk.K_BACKQUOTE): player.equip_weapon("small sword")        
        if ngk.key_pressed(ngk.K_1):
            if shiftisdown():
                if player.invitem in player.get_weapon_names():
                    player.slots[0] = player.invitem
                    ngk.speak(f"You put {player.invitem} in slot 1.")
            else:
                if player.slots[0]: player.equip_weapon(player.slots[0])
                else: ngk.speak("No weapon in that slot.")
        
        if ngk.key_pressed(pygame.K_DELETE): # Cheat/Debug
            n1 = ngk.ui.input_box("What item you want?")
            if n1:
                n2 = ngk.ui.input_box("How many?")
                if n2.isdigit():
                    inv.give(n1, int(n2))
                    ngk.speak(f"Gave {n2} {n1}.")

        if control_pressed() and player.weapontimer.elapsed >= player.weapon.fire_time and not player.reloading:
            player.weapontimer.restart(); w = player.weapon
            # Calculate damage based on range
            damage_to_deal = randint(*w.damage_range)
            # Apply special sword damage logic here
            if w.name == "small sword":
                damage_to_deal = (player.swordsharpness * 3) / 2

            if w.is_melee:
                projectiles.spawn_bullet(player.x, player.y, damage_to_deal, w.range, w.speed, w.name)
            else:
                clip_ammo = player.ammo1.get(w.name, 0)
                if clip_ammo > 0:
                    projectiles.spawn_bullet(player.x, player.y, damage_to_deal, w.range, w.speed, w.name)
                    player.ammo1[w.name] = clip_ammo - 1
                else:
                    if w.get_sound("empty"): play(w.get_sound("empty"))
                
        if control_pressed() and player.reloading: player.weaponjams += 1
        if ngk.key_pressed(pygame.K_r) and not player.reloading: player.reload_weapon()
        if ngk.key_pressed(pygame.K_a) and not player.reloading:
            w = player.weapon
            if w.is_melee:
                ngk.speak("This weapon doesn't take any ammo.")
            else:
                ammo_type = w.sounds.get("ammo_type")
                if not ammo_type:
                    ngk.speak("This weapon has an unknown ammo type.")
                else:
                    clip_ammo = player.ammo1.get(w.name, 0)
                    reserve_ammo = player.inv.get(ammo_type, 0)
                    ngk.speak(f"You have {clip_ammo} in your {w.name}, and {reserve_ammo} {ammo_type} in reserve.")

        if ngk.key_pressed(ngk.K_ESCAPE):
            from main import yesno
            if yesno("Are you sure you want to exit?") == 1: save.writedata(); reset(); from main import mainmenu; mainmenu()

        if player.health <= 0: ngk.dlgplay("death.ogg"); reset(); from main import mainmenu; mainmenu()        
        if player.gathering and player.gathertimer.elapsed >= player.gathertime:
            player.gathertimer.restart(); p.play_stationary("gather.ogg", False); player.gatherprogress += 1
        
        if player.gathering and player.gatherprogress >= player.gatheramount:
            player.gathering = False; player.gatheramount = 0; player.gatherprogress = 0
            player.gatheredtiles.append((player.x, player.y))
            p.play_stationary("gathered.ogg", False)
            tile = gmt()
            gc = randint(1, 9) if tile == "stone" else randint(3, 14)
            p.play_stationary(f"get{tile}.ogg", False); ngk.speak(f"Got {gc} {tile}.")

        if player.xp >= player.xprequired:
            p.play_stationary("level.ogg", False)
            player.level += 1
            # A more balanced XP curve: increase by 25% of the current requirement plus a small bonus per level
            player.xprequired = int(player.xprequired * 1.25) + (player.level * 50)
            
            # Check for resurrection point gain
            if player.level % 10 == 0:
                player.resurrections += 1
                player.update_max_health()
                p.play_stationary("resurrection.ogg", False)
                ngk.speak(f"Resurrection point gained! You now have {player.resurrections}.")
                
        if player.espawntimer.elapsed >= player.espawntime:
            player.espawntimer.restart()
            enemy_type_to_spawn = choice(list(enemies.ENEMY_DATA.keys()))
            enemies.spawn_enemy(randint(0, current_map.maxx), 0, enemy_type_to_spawn)
            
        if player.item_spawn_timer.elapsed >= player.item_spawn_time:
            player.item_spawn_timer.restart()
            world_objects.spawn_random_item()
            
        if player.reloading and player.reloadtimer.elapsed >= player.weapon.reload_time:
            player.reloading = False
            if player.weaponjams > 0: player.weaponjams = 0
        
        if player.weaponjams >= 5:
            player.reloading = False; w_name = player.weapon.name; play("jam.ogg", False)
            inv.give(w_name, -1); inv.give(f"jammed {w_name}", 1)
            if w_name in player.slots: player.slots[player.slots.index(w_name)] = ""
            player.equip_weapon("unarmed")
            ngk.speak("Oh no! Your weapon is jammed! You'll have to fix it."); player.weaponjams = 0
            
        handle_physics()


def handle_physics():
    if player.jumping:
        if player.rising and player.jumpcounter < player.jumpheight and player.jumptimer.elapsed >= player.jumptime and player.y < current_map.maxy:
            player.jumptimer.restart(); player.jumpcounter += 1; player.y += 1
        if player.jumpcounter >= player.jumpheight or player.y >= current_map.maxy:
            player.rising = False; player.lowering = True
        if player.lowering and gmt() == "" and player.falltimer.elapsed >= player.falltime and player.y > 0:
            player.falltimer.restart(); player.jumpcounter -= 1; player.y -= 1; player.fallcounter += 1
        if gmt() != "":
            land_tile = gmt()
            play(f"{land_tile}{'hard' if player.fallcounter > 9 else ''}land.ogg", False)
            if player.fallcounter > 9: player.health -= (player.fallcounter * 2)
            player.rising = player.lowering = player.jumping = False
            player.movetime = player.walktime; player.fallcounter = player.jumpcounter = 0

    if not player.jumping and player.y > 0 and gmt() == "" and not player.falling:
        if player.y > 9: play("fall.ogg", False)
        player.falling = True
    if player.falling and player.falltimer.elapsed >= player.falltime:
        player.falltimer.restart(); player.fallcounter += 1; player.y -= 1
    if gmt() != "" and player.falling:
        player.falling = False; land_tile = gmt()
        play(f"{land_tile}{'hard' if player.fallcounter > 9 else ''}land.ogg", False)
        if player.fallcounter > 9: player.health -= (player.fallcounter * 2)
        player.fallcounter = 0

def playstep():
    tile = gmt()
    if "wall" in tile: play(tile + ".ogg", False); bounce()
    elif tile != "": play(f"{tile}step{randint(1,5)}.ogg", False)

def gmt(): return current_map.get_tile_at(player.x, player.y)
def bounce(): player.x += 1 if player.facing == "left" else -1
def spawn_platform(minx, maxx, y, plattype):
    for i in range(minx, maxx + 1): current_map.tiles[f"{i} {y}"] = plattype

def altisdown(): return ngk.key_down(pygame.K_LALT) or ngk.key_down(pygame.K_RALT)
def shiftisdown(): return ngk.key_down(pygame.K_LSHIFT) or ngk.key_down(pygame.K_RSHIFT)
def control_pressed(): return ngk.key_pressed(pygame.K_LCTRL) or ngk.key_pressed(pygame.K_RCTRL)

def play(path, looping=False):
    if path: return p.play_stationary(path, looping)

def unjamgame(weaponname):
    ngk.speak(f"You begin unjamming your {weaponname}.")
    arrows = [ngk.K_LEFT, ngk.K_RIGHT, ngk.K_DOWN, ngk.K_UP]
    arrow_to_press = choice(arrows); worktimer = ngk.Timer()
    tries, tries_required = 0, randint(7, 13)
    while True:
        enemies.enemy_loop(); projectiles.ebullet_loop(); ngk.process(); pygame.time.wait(5)
        if ngk.key_pressed(arrow_to_press) and worktimer.elapsed >= 500:
            worktimer.restart(); play("unjamming.ogg", False); tries += 1
            arrow_to_press = arrowcheck(arrow_to_press)
        if tries >= tries_required:
            if randint(1, 4) == 4:
                play("unjam.ogg", False); inv.give(f"jammed {weaponname}", -1); inv.give(weaponname, 1)
                ngk.speak(f"You get the {weaponname} back into working order.")
            else:
                ngk.speak("The bullet is too far inside. This gun is a lost cause.")
                inv.give(f"jammed {weaponname}", -1)
            ngk.current_key_pressed = -1
            break

def launch_missile_sequence(item_name):
    """Opens a menu to select an enemy target for a missile."""
    if not enemy_list:
        ngk.speak("No targets available.")
        return

    m = ngk.ui.m_pro()
    m.reset(False)
    m.click_sound = "menuclick.flac"
    m.edge_sound = "menuedge.flac"
    m.enter_sound = "menuenter.flac"

    for enemy in enemy_list:
        enemy_display_name = enemy.enemy_type.replace('_', ' ').title()
        menu_text = f"{enemy_display_name} - Health: {enemy.health}"
        m.add_item_tts(menu_text, enemy)
    
    m.add_item_tts("Cancel", "cancel")
    target = m.run("Select target")

    if target and target != "cancel":
        from world_objects import spawn_guided_missile
        item_data = ITEM_DATA[item_name]
        spawn_guided_missile(target, item_data)
        inv.give(item_name, -1) # Consume the missile
    else:
        ngk.speak("Launch canceled.")

def arrowcheck(a):
    if a == ngk.K_LEFT: return ngk.K_UP
    elif a == ngk.K_UP: return ngk.K_RIGHT
    elif a == ngk.K_RIGHT: return ngk.K_DOWN
    else: return ngk.K_LEFT

def reset():
    p.destroy_all()
    enemies.kill_enemies()
    projectiles.kill_bullets()
    projectiles.kill_ebullets()
    world_objects.kill_sources()
    world_objects.clear_all_world_objects()
    current_map.reset()
    p.destroy_all()

def playsnd(path):
    snd = ngk.snd.Sound()
    snd.load(path)
    snd.play()
    while snd.handle.is_playing:
        enemies.enemy_loop()
        ngk.process()
