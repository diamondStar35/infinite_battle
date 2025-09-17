import ngk
import sys
import os
import json
import game
from player import player
import save

ngk.init()
m = ngk.ui.m_pro()

def get_map_info(map_name):
    """Helper function to peek into a map file for its properties without a full load."""
    map_path = os.path.join("maps", f"{map_name}.json")
    try:
        with open(map_path, 'r') as f:
            data = json.load(f)
            return data.get("properties", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def main():
    f = open("errors.log", "a")
    sys.stderr = f
    ngk.show_window("Infinite Battle")
    save.loaddata()
    ngk.dlg("Welcome to the Infinite Battle! Enjoy!", sound_file="logo.wav")
    mainmenu()

def setupmenu(music=False):
    m.reset(False)
    m.wrap = False
    m.click_sound = "menuclick.ogg"
    m.edge_sound = "menuedge.flac"
    m.enter_sound = "menuenter.ogg"
    if music:
        if not m.music.is_active or not m.music.handle.is_playing:
            m.add_music("menumusic.ogg")
            m.music_added = True
    else:
        m.music_added = False

def mainmenu():
    setupmenu(True)
    m.add_item_tts("Start game", "play")
    m.add_item_tts("Exit", "exit")
    mres = m.run("Infinite Battle,  main menu")
    if mres == "play":
        mapmenu()
    else:
        m.fade_music(20)
        save.writedata()
        ngk.quit()
        sys.exit()

def mapmenu():
    m.reset(False)
    
    available_maps = []
    if os.path.isdir("maps"):
        for filename in os.listdir("maps"):
            if filename.endswith(".json"):
                available_maps.append(os.path.splitext(filename)[0])

    if not available_maps:
        ngk.dlg("No maps found!")
        mainmenu()
        return

    # Only add maps to the menu if the player's level is high enough.
    for map_name in sorted(available_maps):
        info = get_map_info(map_name)
        display_name = info.get("name", map_name.replace("_", " ").title())
        required_level = info.get("required_level", 1)

        if player.level >= required_level:
            m.add_item_tts(display_name, map_name)
    
    m.add_item_tts("Go back", "back")
    mres = m.run("Select map")
    
    if mres == "" or mres == "back":
        mainmenu()
    else:
        m.fade_music(20)
        from map import current_map
        if current_map.load(mres):
            current_map.build_world()
            game.game()
        else:
            ngk.dlg(f"Failed to load map: {mres}")
            mainmenu()

def yesno(q):
    setupmenu(False)
    m.add_item_tts("Yes", "y")
    m.add_item_tts("No", "n")
    mres = m.run(q)
    return 1 if mres == "y" else 2
