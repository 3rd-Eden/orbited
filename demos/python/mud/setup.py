from game import Room
from game import Bot
from game import Item
from roomdata import rooms
from botdata import bots
from itemdata import items

def make_rooms():
    all = {}
    for room in rooms:
        r = Room(**room)
        all[r.name.lower()] = r
    return all

def make_bots():
    all = {}
    for bot in bots:
        b = Bot(**bot)
        all[b.name.lower()] = b
    return all
    
def make_items():
    all = {}
    for item in items:
        i = Item(**item)
        all[i.name.lower()] = i
    return all
    
def setup_all():
    return make_rooms(), make_bots(), make_items()