# A command-line tool for creating and managing game data for Infinite Battle.

import os
import pprint

DATA_FILE_PATH = "data.py"
# A list of all the dictionaries we expect to manage in the data file.
# The order here is the order they will be written back to the file.
MANAGED_DATA_VARS = ["AMMO_DATA", "WEAPON_DATA", "ENEMY_DATA", "ITEM_DATA"]

ITEM_TYPES = [
    'consumable', 
    'explosive', 
    'guided_missile', 
    'interceptor'
]
ITEM_EFFECTS = [
    'heal'
]


def get_input(prompt: str, required: bool = True) -> str:
    """Gets a simple string input from the user."""
    while True:
        value = input(f"> {prompt}: ").strip()
        if value or not required:
            return value
        print("  [!] This field is required.")

def get_validated_integer(prompt: str) -> int:
    """Gets an integer from the user and validates it."""
    while True:
        value_str = get_input(prompt)
        try:
            return int(value_str)
        except ValueError:
            print("  [!] Invalid input. Please enter a whole number.")

def get_validated_float(prompt: str, min_val: float, max_val: float) -> float:
    """Gets a float from the user and validates it is within a given range."""
    while True:
        try:
            value_str = get_input(prompt)
            value = float(value_str)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"  [!] Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("  [!] Invalid input. Please enter a number (e.g., 0.8).")

def get_integer_tuple(prompt: str) -> str:
    """Gets a min and max integer from the user and returns a formatted tuple string."""
    print(f"> {prompt}:")
    min_val = get_validated_integer("  - Enter the minimum value")
    max_val = get_validated_integer("  - Enter the maximum value")
    if min_val > max_val:
        print("  [!] Minimum value was greater than maximum. Swapping them.")
        min_val, max_val = max_val, min_val
    return (min_val, max_val)

def load_data_env():
    """Loads the data file into a dictionary for reading."""
    data_env = {}
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            exec(f.read(), {}, data_env)
        return data_env
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at: {DATA_FILE_PATH}")
        return None
    except Exception as e:
        print(f"[ERROR] Could not parse {DATA_FILE_PATH}. Please fix any syntax errors.")
        print(f"  Details: {e}")
        return None

def validate_entry(entry_key, entry_data, expected_keys):
    """
    Validates a dictionary entry against a set of expected keys.
    Returns a list of validation error messages.
    """
    errors = []
    missing_keys = [key for key in expected_keys if key not in entry_data]
    extra_keys = [key for key in entry_data if key not in expected_keys]

    if missing_keys:
        errors.append(f"  [!] Missing required keys: {', '.join(missing_keys)}")
    
    # We can add more specific validation here in the future if needed,
    # for example, checking if 'damage_range' is a tuple of 2 integers.
    
    return errors

def delete_from_data_file(dict_name: str, key_to_delete: str):
    """
    Loads data, removes a specific key from a dictionary, and rewrites the file.
    """
    data_env = load_data_env()
    if not data_env:
        return

    if dict_name not in data_env or key_to_delete not in data_env[dict_name]:
        print(f"[ERROR] Could not find '{key_to_delete}' in '{dict_name}' to delete.")
        return

    # Delete the key from the dictionary in memory
    del data_env[dict_name][key_to_delete]
    
    try:
        with open(DATA_FILE_PATH, 'w') as f:
            for var_name in MANAGED_DATA_VARS:
                if var_name in data_env:
                    formatted_data = pprint.pformat(
                        data_env[var_name], 
                        indent=4, 
                        width=120, 
                        sort_dicts=False
                    )
                    f.write(f"{var_name} = {formatted_data}\n\n\n")
        
        print(f"\n[SUCCESS] Successfully deleted '{key_to_delete}' from {DATA_FILE_PATH}")
    except IOError as e:
        print(f"\n[ERROR] Could not write to {DATA_FILE_PATH}: {e}")

def view_and_manage_entry(dict_name: str, expected_keys: list):
    """
    Generic function to list, view, validate, and delete an entry from any data dictionary.
    """
    data_env = load_data_env()
    if not data_env or dict_name not in data_env:
        print(f"No data found for {dict_name}.")
        input("Press Enter to continue...")
        return

    target_dict = data_env[dict_name]
    if not target_dict:
        print(f"The dictionary {dict_name} is empty.")
        input("Press Enter to continue...")
        return
        
    entry_keys = list(target_dict.keys())
    selected_key = get_choice_from_menu(f"Select an entry to view from {dict_name}", entry_keys + ["[Go Back]"])
    if selected_key == "[Go Back]" or not selected_key:
        return

    entry_data = target_dict[selected_key]    
    print(f"\n--- Viewing Entry: {selected_key} ---")
    print(pprint.pformat(entry_data, indent=4, width=120, sort_dicts=False))
    
    print("\n--- Validation Report ---")
    errors = validate_entry(selected_key, entry_data, expected_keys)
    if not errors:
        print("  [OK] Entry structure is valid.")
    else:
        for error in errors:
            print(error)

    action = get_choice_from_menu("Choose an action", ["Delete this entry", "Go Back"])    
    if action == "Delete this entry":
        if get_bool_choice(f"Are you sure you want to permanently delete '{selected_key}'?"):
            delete_from_data_file(dict_name, selected_key)
    
    input("\nPress Enter to return to the list menu...")
    view_and_manage_entry(dict_name, expected_keys) # Recursive call to show the list again

def get_choice_from_menu(title: str, options: list) -> str:
    """
    Displays a numbered menu, prompts the user to select an option by number,
    and returns the selected option string.
    """
    if not options:
        return ""

    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice_str = input(f"> Please enter your choice (1-{len(options)}): ")
            if not choice_str:
                continue
            choice_num = int(choice_str)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
            else:
                print(f"  [!] Invalid choice. Please enter a number between 1 and {len(options)}.")
        except (ValueError, IndexError):
            print("  [!] Invalid input. Please enter a number.")

def get_bool_choice(prompt: str) -> bool:
    """Asks a Yes/No question and returns a boolean."""
    choice = get_choice_from_menu(prompt, ["Yes", "No"])
    return choice == "Yes"


def update_data_file(dict_name: str, new_key: str, new_data: dict):
    """
    Loads all data from data.py, updates a specific dictionary, and
    rewrites the entire file with pretty-printed formatting.
    """
    data_env = {}
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            exec(f.read(), {}, data_env)
    except FileNotFoundError:
        print(f"[ERROR] Data file not found at: {DATA_FILE_PATH}")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Could not parse {DATA_FILE_PATH}. Please fix any syntax errors.")
        print(f"  Details: {e}")
        exit(1)

    if dict_name not in data_env:
        print(f"[ERROR] Dictionary '{dict_name}' not found in the data file. Aborting.")
        return
        
    data_env[dict_name][new_key] = new_data

    try:
        with open(DATA_FILE_PATH, 'w') as f:
            for var_name in MANAGED_DATA_VARS:
                if var_name in data_env:
                    formatted_data = pprint.pformat(data_env[var_name], indent=4, width=120, sort_dicts=False)
                    f.write(f"{var_name} = {formatted_data}\n\n")
        
        print(f"\n[SUCCESS] Successfully updated {DATA_FILE_PATH}")
    except IOError as e:
        print(f"\n[ERROR] Could not write to {DATA_FILE_PATH}: {e}")

def create_new_ammo():
    """Guides the user through creating a new ammunition type."""
    print("\n--- Create New Ammunition Type ---")
    print("This will be added to the AMMO_DATA dictionary in data.py.\n")

    internal_key = get_input("Internal Key (e.g., 'shotgun shells')")
    display_name = get_input("Display Name (e.g., 'Shotgun Shells')")
    pickup_sound = get_input("Pickup Sound file (e.g., 'ammo_pickup.ogg')")

    new_ammo_data = {
        "display_name": display_name,
        "pickup_sound": pickup_sound
    }

    update_data_file("AMMO_DATA", internal_key, new_ammo_data)


def create_new_weapon():
    """Guides the user through creating a new weapon, with detailed explanations based on game code."""
    print("\n--- Create New Weapon ---")
    print("This will add a new entry to the WEAPON_DATA dictionary in data.py.\n")

    internal_key = get_input("Internal Key (unique name for this weapon, e.g., 'plasma_rifle')")
    is_melee = get_bool_choice("Is this a melee weapon?")

    print("\n--- Enter Core Weapon Stats ---")
    is_auto = get_bool_choice(
        "Is this weapon automatic?\n"
        "  (A boolean (Yes/No) that flags the weapon as automatic. The game code can use this\n"
        "  to determine if firing should occur continuously when the attack key is held down.)"
    )
    damage_range = get_integer_tuple(
        "Damage Range\n"
        "  (The minimum and maximum damage for a single hit. The game calculates the final\n"
        "  damage by choosing a random integer between these two values via `randint(*damage_range)`.)"
    )
    fire_time = get_validated_integer(
        "Fire Time (Cooldown)\n"
        "  (The cooldown time in milliseconds that must pass after firing before the weapon "
        "  can be fired again."
    )
    weapon_range = get_validated_integer(
        "Effective Range\n"
        "  (The maximum distance in tiles that a projectile will travel before being destroyed."
    )
    speed = get_validated_integer(
        "Projectile Speed\n"
        "  (The travel time in milliseconds for the weapon's projectile to move one tile.\n"
        "  A LOWER number results in a FASTER projectile."
    )

    if is_melee:
        # Melee weapons have no ammo or reload time according to the game logic.
        max_ammo = 0
        reload_time = 0
        ammo_type = None
    else:
        print("\n--- Enter Ranged Weapon Stats ---")
        max_ammo = get_validated_integer(
            "Max Ammo (Clip Size)\n"
            "  (The maximum number of rounds the weapon can hold in its clip. The `reload_weapon`\n"
            "  function in `player.py` uses this to determine if the weapon is full.)"
        )
        reload_time = get_validated_integer(
            "Reload Time\n"
            "  (The total duration in milliseconds for the reload cycle. The `player.reloading`\n"
            "  state will be active for this amount of time, during which the player cannot fire.)"
        )
        
        # Load existing ammo types to let the user choose.
        data_env = {}
        try:
            with open(DATA_FILE_PATH, 'r') as f:
                exec(f.read(), {}, data_env)
            ammo_options = list(data_env.get("AMMO_DATA", {}).keys())
            if not ammo_options:
                print("\n[WARNING] No ammo types found in AMMO_DATA. You must enter one manually.")
                ammo_type = get_input("Ammo Type (must match a key in AMMO_DATA)")
            else:
                ammo_type = get_choice_from_menu("Select the Ammo Type for this weapon", ammo_options)
        except Exception as e:
            print(f"\n[ERROR] Could not read ammo types from data.py: {e}")
            print("You will have to enter the ammo type manually.")
            ammo_type = get_input("Ammo Type (must match a key in AMMO_DATA)")

    print("\n--- Enter Sound File Names ---")
    sounds_dict = {}
    sounds_dict['draw'] = get_input(
        "Draw Sound (Played once when the player equips this weapon.",
        required=False
    )
    sounds_dict['fire'] = get_input(
        "Fire Sound (Played each time a projectile is created for this weapon.)"
    )
    
    hit_sounds_list = []
    print("> Enter one or more hit sounds. Press Enter on an empty line when finished.")
    print("  (A sound from this list is played at random when this weapon's projectile hits an enemy.)")
    while True:
        hit_sound = get_input(f"  - Hit sound {len(hit_sounds_list) + 1}", required=False)
        if not hit_sound:
            break
        hit_sounds_list.append(hit_sound)
    sounds_dict['hit_sounds'] = hit_sounds_list
    
    sounds_dict['empty'] = get_input(
        "Empty Clip Sound (Played when trying to fire a non-melee weapon with 0 clip ammo)",
        required=False
    )
    sounds_dict['reload'] = get_input(
        "Reload Sound (Played once at the start of the reload sequence)",
        required=False
    )

    if ammo_type:
        sounds_dict['ammo_type'] = ammo_type

    new_weapon_data = {
        'auto': is_auto,
        'damage_range': damage_range,
        'fire_time': fire_time,
        'max_ammo': max_ammo,
        'melee': is_melee,
        'range': weapon_range,
        'reload_time': reload_time,
        'sounds': sounds_dict,
        'speed': speed,
    }

    update_data_file("WEAPON_DATA", internal_key, new_weapon_data)


def create_new_item():
    """Guides the user through creating a new item with mechanic-based explanations."""
    print("\n--- Create New Item ---")
    print("This will add a new entry to the ITEM_DATA dictionary in data.py.\n")

    internal_key = get_input("Internal Key (unique name for this item, e.g., 'stimpack')")
    
    # This will be the main dictionary we build and then write to the file.
    new_item_data = {}

    item_type = get_choice_from_menu("Select the fundamental type of this item", ITEM_TYPES)
    new_item_data['type'] = item_type

    if item_type == 'consumable':
        print("\n--- Consumable Item Properties ---")
        effect = get_choice_from_menu("Select the effect of this consumable", ITEM_EFFECTS)
        new_item_data['effect'] = effect
        
        if effect == 'heal':
            new_item_data['value_range'] = get_integer_tuple(
                "Healing Amount\n"
                "  (The minimum and maximum health points restored to the player upon use.)"
            )
        
        new_item_data['sound'] = get_input(
            "Use Sound\n"
            "  (The sound that plays when the player consumes this item.)"
        )

    elif item_type == 'explosive':
        print("\n--- Explosive Item Properties ---")
        new_item_data['detonation_time'] = get_validated_integer(
            "Detonation Time\n"
            "  (The time in milliseconds from when the item is used until it explodes.)"
        )
        new_item_data['blast_radius'] = get_validated_integer(
            "Blast Radius\n"
            "  (The maximum distance in tiles from the explosion's center that damage can be dealt.)"
        )
        new_item_data['damage_range'] = get_integer_tuple(
            "Damage Range\n"
            "  (The minimum and maximum damage dealt at the explosion's epicenter.)"
        )
        new_item_data['damage_falloff'] = get_bool_choice(
            "Enable Damage Falloff?\n"
            "  (If 'Yes', the explosion will deal less damage to targets farther from the center of the blast.)"
        )
        
        print("\n--- Explosive Sounds ---")
        sounds_dict = {}
        sounds_dict['throw'] = get_input("Throw Sound (Played when the item is activated/thrown by the player.)")
        sounds_dict['fuse'] = get_input("Fuse Sound (A looping sound that plays during the detonation countdown.)")
        sounds_dict['explode'] = get_input("Explode Sound (Played once when the item detonates.)")
        new_item_data['sounds'] = sounds_dict

    elif item_type == 'guided_missile':
        print("\n--- Guided Missile Properties ---")
        new_item_data['speed'] = get_validated_integer(
            "Missile Speed\n"
            "  (The travel time in milliseconds for the missile to move one tile. A LOWER value is FASTER.)"
        )
        new_item_data['blast_radius'] = get_validated_integer(
            "Blast Radius\n"
            "  (The maximum distance in tiles from the missile's impact that damage can be dealt.)"
        )
        new_item_data['damage_range'] = get_integer_tuple(
            "Damage Range\n"
            "  (The minimum and maximum damage dealt to all targets within the blast radius.)"
        )
        
        print("\n--- Missile Sounds ---")
        sounds_dict = {}
        sounds_dict['launch'] = get_input("Launch Sound (Played when the missile is fired.)")
        sounds_dict['travel'] = get_input("Travel Sound (A looping sound that plays while the missile is in flight.)")
        sounds_dict['warning'] = get_input("Warning Sound (Played when the missile gets close to the player.)")
        sounds_dict['explode'] = get_input("Explode Sound (Played once upon impact.)")
        new_item_data['sounds'] = sounds_dict

    elif item_type == 'interceptor':
        print("\n--- Interceptor Properties ---")
        new_item_data['range'] = get_validated_integer(
            "Interception Range\n"
            "  (The detection radius in tiles. An incoming missile within this range of the player will be destroyed.)"
        )
        new_item_data['duration'] = get_validated_integer(
            "Active Duration\n"
            "  (How long in milliseconds the interceptor field will remain active, searching for missiles.)"
        )

        print("\n--- Interceptor Sounds ---")
        sounds_dict = {}
        sounds_dict['activate'] = get_input("Activation Sound (Played when the interceptor is deployed.)")
        sounds_dict['intercept'] = get_input("Intercept Sound (Played when a missile is successfully destroyed.)")
        new_item_data['sounds'] = sounds_dict
        
    # Common Properties (Applies to all item types) ---
    print("\n--- Common Item Properties ---")
    new_item_data['pickup_sound'] = get_input(
        "Pickup Sound\n"
        "  (The sound played when the player picks this item up from the ground.)"
    )

    update_data_file("ITEM_DATA", internal_key, new_item_data)


def create_new_enemy():
    """Guides the user through creating a new enemy with mechanic-based explanations."""
    print("\n--- Create New Enemy ---")
    print("This will add a new entry to the ENEMY_DATA dictionary in data.py.\n")

    # We need weapon and item lists to present choices to the user.
    data_env = {}
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            exec(f.read(), {}, data_env)
    except Exception:
        # If the file can't be read, we'll have to rely on manual input.
        pass
    
    weapon_options = list(data_env.get("WEAPON_DATA", {}).keys())
    item_options = list(data_env.get("ITEM_DATA", {}).keys())
    # 'coin' is a special loot type handled in code, so we add it manually.
    loot_options = ['coin'] + item_options

    # Basic Info ---
    internal_key = get_input("Internal Key (unique name for this enemy, e.g., 'heavy_trooper')")
    new_enemy_data = {}

    print("\n--- Enter Core Enemy Stats ---")
    new_enemy_data['health_range'] = get_integer_tuple(
        "Health Range\n"
        "  (The enemy's base health. The final health on spawn will be a random value\n"
        "  from this range, multiplied by the player's current level.)"
    )
    new_enemy_data['xp_range'] = get_integer_tuple(
        "XP Reward Range\n"
        "  (The minimum and maximum experience points the player receives for defeating this enemy.)"
    )
    new_enemy_data['fire_time'] = get_validated_integer(
        "Attack Cooldown\n"
        "  (The time in milliseconds the enemy must wait after attacking before it can attack again.)"
    )
    
    print("\n--- Enter Combat Stats ---")
    new_enemy_data['walk_speed'] = get_integer_tuple(
        "Walk Speed (Time Between Steps)\n"
        "  (The minimum and maximum time in milliseconds the enemy waits between taking each step.\n"
        "  A LOWER value means a FASTER moving enemy.)"
    )
    new_enemy_data['detection_range'] = get_validated_integer(
        "Detection Range\n"
        "  (The distance in tiles at which the enemy will detect the player and switch\n"
        "  from idle wandering to active combat behavior.)"
    )

    # Weapon Selection ---
    print("\n--- Select Enemy Weapons ---")
    print("  (The enemy will randomly choose one of these weapons on spawn. The weapon's\n"
          "  stats (damage, range, etc.) will be used for the enemy's attacks.)")
    enemy_weapons = []
    if not weapon_options:
        print("[WARNING] No weapons found in WEAPON_DATA. You must enter names manually.")
        while True:
            weapon_name = get_input("Enter weapon key (or leave empty to finish)", required=False)
            if not weapon_name: break
            enemy_weapons.append(weapon_name)
    else:
        while True:
            # Allow adding more weapons or finishing
            menu_options = weapon_options + ["[Done Adding Weapons]"]
            choice = get_choice_from_menu("Select a weapon to add", menu_options)
            if choice == "[Done Adding Weapons]":
                break
            enemy_weapons.append(choice)
            print(f"  Added '{choice}'. Current weapons: {enemy_weapons}")

    if not enemy_weapons:
        print("[WARNING] No weapons were selected for the enemy.")
    new_enemy_data['weapons'] = enemy_weapons

    print("\n--- Create Loot Table ---")
    loot_table = {}
    while get_bool_choice("Do you want to add a loot drop item?"):
        if not loot_options:
            print("[WARNING] No items found to add as loot. Please enter manually.")
            item_name = get_input("Enter loot item name (e.g., 'coin', 'health drink')")
        else:
            item_name = get_choice_from_menu("Select the item to drop", loot_options)
        
        print(f"\nConfiguring drop for: '{item_name}'")
        loot_info = {}
        loot_info['amount_range'] = get_integer_tuple(
            "Amount Range\n"
            "  (The min/max quantity of this item that drops if the drop is successful.)"
        )
        loot_info['chance'] = get_validated_float(
            "Drop Chance\n"
            "  (The probability from 0.0 to 1.0 that this item will drop. For example,\n"
            "  0.8 means an 80% chance.)",
            min_val=0.0, max_val=1.0
        )
        loot_table[item_name] = loot_info
    new_enemy_data['loot'] = loot_table

    print("\n--- Define Usable Items ---")
    usable_items = {}
    while get_bool_choice("Allow this enemy to use an item?"):
        item_name = get_choice_from_menu("Select the item to allow", item_options) if item_options else get_input("Enter usable item name")
        print(f"\nConfiguring usage for: '{item_name}'")
        conditions = {}
        if item_name == 'health drink':
            conditions['health_threshold'] = get_validated_float(
                "Health Threshold\n"
                "  (The enemy will attempt to use this item when its health drops below this\n"
                "  percentage (e.g., 0.4 for 40% health).)", 0.0, 1.0
            )
        conditions['chance'] = get_validated_float("Use Chance (0.0 to 1.0) This determines the chance for using this item. Higher chance will result in a higher probability of using this item.", 0.0, 1.0)
        usable_items[item_name] = conditions
    new_enemy_data['usable_items'] = usable_items

    # Sound Data ---
    print("\n--- Enter Sound File Names ---")
    sounds_dict = {}
    sounds_dict['death'] = get_input(
        "Death Sound\n"
        "  (Played once when the enemy's health reaches zero.)"
    )
    hit_sounds_list = []
    print("> Enter one or more hit sounds. Press Enter on an empty line when finished.")
    print("  (A sound from this list is played at random when this enemy is damaged by the player.)")
    while True:
        hit_sound = get_input(f"  - Hit sound {len(hit_sounds_list) + 1}", required=False)
        if not hit_sound:
            break
        hit_sounds_list.append(hit_sound)
    sounds_dict['hit_sounds'] = hit_sounds_list

    walk_sounds_list = []
    print("> Enter one or more walk sounds (Overrides default tile sounds). Press Enter on an empty line to finish.")
    while True:
        walk_sound = get_input(f"  - Walk sound {len(walk_sounds_list) + 1}", required=False)
        if not walk_sound: break
        walk_sounds_list.append(walk_sound)
    sounds_dict['walk_sounds'] = walk_sounds_list
    
    voices_list = []
    print("> Enter one or more voice sounds. A random sound will be played periodically while idle or in combat. Press Enter on an empty line to finish.")
    while True:
        voice = get_input(f"  - Voice sound {len(voices_list) + 1}", required=False)
        if not voice: break
        voices_list.append(voice)
    sounds_dict['voices'] = voices_list
    
    new_enemy_data['sounds'] = sounds_dict

    update_data_file("ENEMY_DATA", internal_key, new_enemy_data)


def list_manager_hub():
    """Main menu for the listing/management functionality."""
    while True:
        title = "List, View, and Manage Data"
        options = [
            "List Ammunition Types",
            "List Weapons",
            "List Items",
            "List Enemies",
            "Go Back to Main Menu"
        ]
        choice = get_choice_from_menu(title, options)
        if choice == "List Ammunition Types":
            expected_keys = ["display_name", "pickup_sound"]
            view_and_manage_entry("AMMO_DATA", expected_keys)
        elif choice == "List Weapons":
            expected_keys = ["auto", "damage_range", "fire_time", "max_ammo", "melee", "range", "reload_time", "sounds", "speed"]
            view_and_manage_entry("WEAPON_DATA", expected_keys)
        elif choice == "List Items":
            expected_keys = ["type", "pickup_sound"] 
            print("[INFO] Item validation is basic and only checks for common keys.")
            view_and_manage_entry("ITEM_DATA", expected_keys)
        elif choice == "List Enemies":
            expected_keys = ["health_range", "xp_range", "fire_time", "walk_speed", "detection_range", "weapons", "loot", "usable_items", "sounds"]
            view_and_manage_entry("ENEMY_DATA", expected_keys)
        elif choice == "Go Back to Main Menu":
            break

def main():
    """Main function to run the toolkit."""
    while True:
        title = "Infinite Battle: Data Creation Toolkit"
        options = [
            "Create New Ammunition Type",
            "Create New Weapon",
            "Create New Item",
            "Create New Enemy",
            "Manage Data",
            "[Exit]"
        ]
        
        choice = get_choice_from_menu(title, options)

        if choice == "Create New Ammunition Type":
            create_new_ammo()
        elif choice == "Create New Weapon":
            create_new_weapon()
        elif choice == "Create New Item":
            create_new_item()
        elif choice == "Create New Enemy":
            create_new_enemy()
        elif choice == "Manage Data":
            list_manager_hub()
        elif choice == "[Exit]" or choice == "":
            print("Exiting toolkit.")
            break

if __name__ == "__main__":
    main()
