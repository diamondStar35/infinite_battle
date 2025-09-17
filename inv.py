import ngk
from player import player
from random import randint
from data import ITEM_DATA, AMMO_DATA

def give(item, amount=1):
    player.give_item(item, amount)

def cycle_inv(dir):
    player.cycle_inventory(dir)

def useitem():
    keys = player.get_inventory_keys()
    if keys and player.invpos < len(keys):
        item_name = keys[player.invpos]
        use(item_name)
    else:
        ngk.speak("No items to use.")

def use(item_name):
    # Check if the item is a weapon first
    if item_name in player.get_weapon_names():
        player.equip_weapon(item_name)
        return

    # Check for special case items
    if item_name.startswith("jammed"):
        regitem = item_name.split(" ", 1)[1]
        from game import unjamgame
        unjamgame(regitem)
        return

    if item_name in AMMO_DATA:
        ngk.speak(f"This is {item_name}. Reload a compatible weapon to use it.")
        return

        
    # Process items from ITEM_DATA
    if item_name in ITEM_DATA:
        item_data = ITEM_DATA[item_name]        
        item_type = item_data.get("type")
        effect = item_data.get("effect")
        if item_type == "explosive":
            from world_objects import spawn_explosive
            spawn_explosive(player.x, player.y, item_data)
            give(item_name, -1)
            ngk.speak(f"You activate {item_name}. Run away quickly.")
            return

        elif item_type == "guided_missile":
            from game import launch_missile_sequence
            launch_missile_sequence(item_name)
            return

        elif item_type == "interceptor":
            from world_objects import spawn_interceptor_field
            spawn_interceptor_field(item_data)
            give(item_name, -1)
            return

        elif item_type == "consumable":
            effect = item_data.get("effect")
            if effect == "heal":
                heal_amount = randint(*item_data["value_range"])
                player.health += heal_amount
                if player.health > player.max_health:
                    player.health = player.max_health
                ngk.speak(f"You healed for {heal_amount} health.")

            # Play sound (for all consumables)
            sound = item_data.get("sound")
            if sound:
                from game import playsnd
                playsnd(sound)

            # Post-use actions (for all consumables)
            from world_objects import spawn_can
            spawn_can(player.x, player.y)
            give(item_name, -1)
            return
