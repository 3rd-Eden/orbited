rooms = [
    {#M
        'name': 'The Lobby',
        'description': 'A large hall.',
        'north': 'the kitchen',
        'south': "the men's room",
        'east': "the janitor's closet",
        'up': 'the classroom',
        'directions': ['North', 'South', 'East', 'Up'],
    },
    {#K
        'name': 'The Kitchen',
        'description': 'A noisy kitchen.',
        'south': 'the lobby',
        'east': 'the media studies library',
        'directions': ['South', 'East'],
    },
    {#R
        'name': "The Men's Room",
        'description': 'A smelly bathroom.',
        'north': 'the lobby',
        'west': 'a filthy stall',
        'east': 'the urinal',
        'directions': ['North', 'East', 'West'],
    },
    {#F
        'name': 'A Filthy Stall',
        'description': 'You hold your nose.',
        'east': "the men's room",
        'directions': ['East'],
    },
    {#U
        'name': 'The Urinal',
        'description': 'The urinal is filled with paper towels. There seems to be something else, too.',
        'west': "the men's room",
        'directions': ['West'],
    },
    {#L
        'name': 'The Media Studies Library',
        'description': 'Dusty books line the walls.',
        'west': 'the kitchen',
        'down': 'the media studies dungeon',
        'directions': ['West', 'Down'],
    },
    {#C
        'name': 'The Classroom',
        'description': 'This room is currently in the throes of an electrical storm.',
        'down': 'the lobby',
        'directions': ['Down'],
    },
    {#J
        'name': "The Janitor's Closet",
        'description': 'This room is cramped.',
        'west': 'the lobby',
        'down': 'the basement',
        'directions': ['West', 'Down'],
    },
    {#B
        'name': 'The Basement',
        'description': "It's dark down here!",
        'up': "the janitor's closet",
        'directions': ['Up'],
    },
    {#D
        'name': 'The Media Studies Dungeon',
        'description': 'Whips and handcuffs line the walls, which seem to have leather wallpaper.',
        'up': 'the media studies library',
        'directions': ['Up'],
    },
    {#S
        'name': 'The Media Studies Secret Room',
        'description': "No one knows you're here. If they knew, they probably would have taken better care of their belongings...",
        'south': 'the media studies dungeon',
        'directions': ['South'],
    }
]

#       S
#   K L\D
# C\M J\B
# F R U