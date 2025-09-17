# This file acts as an internal database for game objects.
# It is not intended to be edited by the end-user.

# A list of all ammo types in the game.
AMMO_DATA = {
    "revolver cartridges": {
        "display_name": "Revolver Cartridges",
        "pickup_sound": "ammo_pickup.ogg"
    },
    "heavy machinegun belt": {
        "display_name": "Heavy Machinegun Belt",
        "pickup_sound": "ammo_pickup.ogg"
    }
}


WEAPON_DATA = {
    'mk44 machinegun': {
        'auto': False,
        'damage_range': (180, 220),
        'fire_time': 20,
        'max_ammo': 500,
        'melee': False,
        'range': 100,
        'reload_time': 200,
        'sounds': {
            'draw': 'draw.ogg',
            'empty': 'empty.ogg',
            'fire': 'fire.ogg',
            'hit_sounds': ['hit1.ogg', 'hit2.ogg', 'hit3.ogg'],
            'reload': 'reload.ogg',
            'ammo_type': 'heavy machinegun belt'
        },
        'speed': 20
    },
    'revolver': {
        'auto': True,
        'damage_range': (40, 70),
        'fire_time': 100,
        'max_ammo': 50,
        'melee': False,
        'range': 6,
        'reload_time': 1990,
        'sounds': {
            'draw': 'revolverdraw.ogg',
            'empty': 'revolverempty.ogg',
            'fire': 'revolver.ogg',
            'hit_sounds': ['revolverhit1.ogg', 'revolverhit2.ogg'],
            'reload': 'revolverreload.ogg',
            'ammo_type': 'revolver cartridges'
        },
        'speed': 30
    },
    'small sword': {
        'auto': False,
        'damage_range': (2, 4),
        'fire_time': 500,
        'max_ammo': 0,
        'melee': True,
        'range': 2,
        'reload_time': 0,
        'sounds': {
            'draw': 'small sworddraw.ogg',
            'empty': '',
            'fire': 'small sword.ogg',
            'hit_sounds': ['small swordhit1.ogg', 'small swordhit2.ogg', 'small swordhit3.ogg'],
            'reload': ''
        },
        'speed': 40
    },
    'unarmed': {
        'auto': False,
        'damage_range': (1, 2),
        'fire_time': 500,
        'max_ammo': 0,
        'melee': True,
        'range': 1,
        'reload_time': 0,
        'sounds': {
            'draw': '',
            'empty': '',
            'fire': 'punch.ogg',
            'hit_sounds': ['punch_hit.ogg'],
            'reload': ''
        },
        'speed': 10
    }
}

ENEMY_DATA = {
    'grunt': {
        'damage': 8,
        'fire_time': 1200,
        'health_range': (16, 42),
        'is_melee': False,
        'loot': {'coin': {'amount_range': (3, 20), 'chance': 0.8}},
        'range': 6,
        'sounds': {
            'death': 'e1death.ogg',
            'hit_sounds': ['e1hit1.ogg', 'e1hit2.ogg', 'e1hit3.ogg']
        },
        'speed': 100,
        'weapons': ['revolver'],
        'xp_range': (20, 60)
    },
    'swordsman': {
        'damage': 12,
        'fire_time': 600,
        'health_range': (25, 55),
        'is_melee': True,
        'loot': {
            'coin': {'amount_range': (10, 35), 'chance': 0.9},
            'health drink': {'amount_range': (1, 1), 'chance': 0.15}
        },
        'range': 2,
        'sounds': {
            'death': 'e1death.ogg',
            'hit_sounds': ['e1hit1.ogg', 'e1hit2.ogg', 'e1hit3.ogg']
        },
        'speed': 40,
        'weapons': ['small sword'],
        'xp_range': (400, 800)
    }
}

ITEM_DATA = {
    'health drink': {
        'type': 'consumable',
        'effect': 'heal',
        'value_range': (30, 60),
        'sound': 'healthdrink.ogg',
        'pickup_sound': 'item_pickup.ogg'
    },
    'frag grenade': {
        'type': 'explosive',
        'detonation_time': 3000,
        'blast_radius': 8,
        'damage_range': (80, 150),
        'damage_falloff': True,
        'sounds': {
            'throw': 'grenade_throw.ogg',
            'fuse': 'grenade_fuse.ogg',
            'explode': 'grenade_explode.ogg'
        },
        'pickup_sound': 'item_pickup.ogg' # New
    },
    'pipe bomb': {
        'type': 'explosive',
        'detonation_time': 5000,
        'blast_radius': 12,
        'damage_range': (150, 250),
        'damage_falloff': True,
        'sounds': {
            'throw': 'canthrow.ogg',
            'fuse': 'pipebomb_fuse.ogg',
            'explode': 'pipebomb_explode.ogg'
        },
        'pickup_sound': 'item_pickup.ogg'
    },
    'guided missile': {
        'type': 'guided_missile',
        'speed': 80,                  # Milliseconds per tile moved
        'blast_radius': 6,
        'damage_range': (2000, 3000),
        'sounds': {
            'launch': 'missile_launch.ogg',
            'travel': 'missile_travel.ogg',  # A looping sound
            'warning': 'missile_warning.ogg',# Plays when near player
            'explode': 'missile_explode.ogg'
        },
        'pickup_sound': 'item_pickup.ogg'
    },
    'missile interceptor': {
        'type': 'interceptor',
        'range': 12,                  # Tiles in front/behind player
        'duration': 4000,             # Milliseconds active
        'sounds': {
            'activate': 'interceptor_on.ogg',
            'intercept': 'interceptor_hit.ogg'
        },
        'pickup_sound': 'item_pickup.ogg'
    }
}
