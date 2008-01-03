from debug import debug
import random
directions = {'north':'the south', 'south':'the north', 'east':'the west', 'west':'the east', 'up':'below', 'down':'above', 'into the void':'the void'}
verbs = {' misses ':' miss ', ' hits ':' hit ',' plunges ':' plunge ', ' whips ':' whip ',' stabs ':' stab '}
unique_items1 = ['shoes', 'pants']
unique_items2 = ['shirt', 'cape']
unique_items3 = ['shield', 'weapon']
PING_TRIGGER_VALUE = 5
PING_CLOCK_MAX = 7

class Room:
    def __init__(self, name, description, north=None, south=None, east=None, west=None, up=None, down=None, directions=[]):
        self.name = name
        self.description = description
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.up = up
        self.down = down
        self.directions = directions
        self.occupants = []
        self.items = []
    
    def action(self, person, str):
        for p in self.occupants:
            p.say('GOD', person, str, str)
    
    def join(self, person, direction):
        person.joined(self, direction)
        for p in self.occupants:
            p.say('JOIN', person, directions[direction])
        self.occupants.append(person)
            
    def leave(self, person, direction):
        try:
            self.occupants.remove(person)
        except:
            debug( 'DEAD PERSON NOT IN ROOM.OCCUPANTS! line 31')
        for p in self.occupants:
            p.say('LEAVE', person, direction)
            
    def say(self, person, msg):
        for p in self.occupants:
            p.say('PUBLIC', person, msg)
            
    def get(self, person, item):
        for p in self.occupants:
            p.say('GET', person, item)
    
    def drop(self, person, item, normal=True, message1=None, message2=None):
        for p in self.occupants:
            if normal:
                p.say('DROP', person, item)
            else:
                p.say('GOD', person, message1, message2)
            
    def attack(self, attacker, target):
        for p in self.occupants:
            p.say('ATTACK', attacker, target)
    
    def die(self, person):
        for p in self.occupants:
            p.say('GOD', person, 'You die!', '%s dies!' % person.name)
        self.leave(person, 'into the void')
            
    def combat(self, one, two):
        r = []
        r.append([one.name, one.hp, two.name, two.hp])
        r.append(self.hit(one,two))
        r.append(self.hit(two,one))
        for p in self.occupants:
            thelist = r
            if p == one:
                thelist = [['YOU',r[0][1],r[0][2],r[0][3]],['YOU',verbs[r[1][1]],r[1][2],r[1][3]],[r[2][0],r[2][1],'YOU',r[2][3]]]
            elif p == two:
                thelist = [[r[0][0],r[0][1],'YOU',r[0][3]],[r[1][0],r[1][1],'YOU',r[1][3]],['YOU',verbs[r[2][1]],r[2][2],r[2][3]]]
            p.say('COMBAT', thelist)
            
    def hit(self, one, two):
        a = one.attack
        b = two.defense
        rand = a
        if b > a:
            rand = b
        attack = a + random.randint(1,rand)
        defense = b + random.randint(1,rand)
        damage = attack - defense
        verb = one.attack_verb
        if damage < 1:
            damage = 0
            verb = ' misses '
        two.hp -= damage
        return [one.name, verb, two.name, damage]
        
class Item:
    def __init__(self, name, description=' is here', location=None, type='weapon', verb=' hits ', attack=0, defense=0, special=None, charge=1, take=True):
        self.name = name
        self.description = description
        self.location = location
        self.type = type
        self.verb = verb
        self.attack = attack
        self.defense = defense
        self.special = special
        self.fullcharge = charge
        self.charge = charge
        self.take = take
        
    def use(self, target):
        result = 'Nothing happens.'
        if self.type == 'key':
            if self.special == target.name:
                result = target.special[0]
                if target.special[1] == 'door':
                    setattr(target.location, target.special[2][0], target.special[2][1])
                    target.location.directions.append(target.special[2][0].title())
                elif target.special[1] == 'game over':
                    return result, 1337
        elif self.type == 'spell':
            result = self.special[0]
            setattr(target, self.special[1], getattr(target, self.special[1]) + self.special[2])
            self.charge -= 1
            if not self.charge:
                msg = '%s disappears in a puff of smoke!' % self.name
                self.location.drop(self, False, msg, msg)
        return result, self.charge
        
    def eat(self):
        result = "That's not food"
        if self.type == 'food':
            result = self.special[0]
            guy = self.location
            setattr(guy, self.special[1], getattr(guy, self.special[1]) + self.special[2])
            self.location.drop(self, False, 'You eat %s' % self.name, '%s eats %s' % (self.location.name, self.name))
        return result
            
class Person:
    def __init__(self, name):
        self.name = name
    
    def joined(self, room, direction):
        self.location = room
        
    def die(self, rand_room, resurrect=True):
        for item in self.items:
            self.drop(item)
        self.location.die(self)
        if resurrect:
            self.hp = self.basehp
            self.attack = self.baseattack
            self.defense = self.basedefense
            rand_room.join(self, 'into the void')
        elif isinstance(self, Player):
            self.orbit.event([self.user_key], ['restart'])
        
    def get(self, item):
        if not isinstance(self, Bot):
            if not item.take:
                return self.orbit.event([self.user_key], ['GOD', "It won't budge"])
            elif item.type in unique_items1:
                for object in self.items:
                    if object.type == item.type:
                        return self.orbit.event([self.user_key], ['GOD', "You're already wearing %s" % item.type])
            elif item.type in unique_items2:
                for object in self.items:
                    if object.type == item.type:
                        return self.orbit.event([self.user_key], ['GOD', "You're already wearing a %s" % item.type])
            elif item.type in unique_items3:
                for object in self.items:
                    if object.type == item.type:
                        return self.orbit.event([self.user_key], ['GOD', "You're already holding a %s" % item.type])
        try:
            item.location.items.remove(item)
        except:
            pass
        item.location = self
        self.items.append(item)
        self.location.get(self,item)
        self.attack += item.attack
        self.defense += item.defense
        if item.type == 'weapon':
            self.attack_verb = item.verb
        if isinstance(self, Bot):
            item.charge = item.fullcharge
        
    def drop(self, item, normal=True, message1=None, message2=None):
        self.items.remove(item)
        if normal:
            item.location = self.location
            self.location.items.append(item)
        else:
            item.location = None
        self.location.drop(self,item,normal,message1,message2)
        self.attack -= item.attack
        self.defense -= item.defense
        if item.type == 'weapon':
            self.attack_verb = ' hits '
        
    def say(self, cmd, *args):
        return getattr(self, 'say_%s'%cmd)(*args)
        
    def say_JOIN(self, who, direction):
        pass
        
    def say_LEAVE(self, who, direction):
        pass
        
    def say_PUBLIC(self, who, msg):
        pass
        
    def say_PRIV(self, who, msg):
        pass
        
    def say_GET(self, who, item):
        pass
        
    def say_DROP(self, who, item):
        pass
        
    def say_ATTACK(self, attacker, target):
        pass
        
    def say_COMBAT(self, roundlist):
        pass

    def say_GOD(self, person, msg1, msg2):
        pass
        
class Bot(Person):
    def __init__(self, name, description=' growls.', location=None, phrases=None, greeting=None, triggers=None, mobile=0, aggressive=0, attack=5, defense=5, hp=10):
        self.name = name
        self.description = description
        self.location = location
        self.phrases = phrases
        self.greeting = greeting
        self.triggers = triggers
        self.mobile = mobile
        self.aggressive = aggressive
        self.baseattack = attack
        self.attack = attack
        self.basedefense = defense
        self.defense = defense
        self.basehp = hp
        self.hp = hp
        self.attack_verb = ' hits '
        self.items = []
        
    def move(self, clock):
        if self.mobile and not clock % self.mobile:
            dir = random.choice(self.location.directions).lower()
            self.location.leave(self, dir)
            return getattr(self.location, dir), self, dir
        return 0, 0, 0
        
    def fight(self, clock):
        if self.aggressive and not clock % self.aggressive and len(self.location.occupants) > 1:
            target = random.choice(self.location.occupants)
            while target == self:
                target = random.choice(self.location.occupants)
            self.location.attack(self, target)
            return [self, target]
        return False
        
    def say_JOIN(self, who, direction):
        if self.greeting:
            who.say('PRIV', self, self.greeting)
        
    def say_PRIV(self, who, msg):
        if isinstance(who, Bot):
            return
        noReply = True
        if self.triggers:
            for word in msg.lower().split(' '):
                if word in self.triggers:
                    who.say('PRIV', self, self.triggers[word][0])
                    if len(self.triggers[word]) > 1:
                        if self.triggers[word][1] == 'drop':
                            for item in self.items:
                                if item.name == self.triggers[word][2]:
                                    self.drop(item)
                        else:
                            pass
                    noReply = False
        if noReply and self.phrases:
            who.say('PRIV', self, random.choice(self.phrases))
        
class Player(Person):
    def __init__(self, name, key, orbit, attack=5, defense=5, hp=30):
        self.name = name
        self.user_key = key
        self.orbit = orbit
        self.baseattack = attack
        self.attack = attack
        self.basedefense = defense
        self.defense = defense
        self.basehp = hp
        self.hp = hp
        self.location = None
        self.description = ' stands here'
        self.attack_verb = ' hits '
        self.items = []
        self.ping_count = 0

    def change_description(self, new_description):
        self.description = new_description
        self.orbit.event([self.user_key], ['GOD', 'description set'])
        
    def ping_reply(self):
        self.ping_count = 0
        
    def send_ping(self):
        self.ping_count += 1
        if self.ping_count == PING_TRIGGER_VALUE:
            self.orbit.event([self.user_key], ['ping', self.name])
        if self.ping_count == PING_CLOCK_MAX:
            self.die(self.location, False)
            return True        return False
        
    def joined(self, room, direction):
        self.location = room
        if direction == 'into the void':
            joinlist = ['You', ' appear ', 'in a blaze of confetti']
        else:
            joinlist = ['You', ' go ', direction]
        self.orbit.event([self.user_key], ['JOINLEAVE', joinlist])
        self.look_room()
        
    def look_items(self):
        itemlist = []
        for item in self.items:
            itemlist.append([item.name, ' (%s)' % item.type])
        self.orbit.event([self.user_key], ['INVENTORY', itemlist])
        
    def who(self, peeps):
        wholist = []
        for guy in peeps.values():
            wholist.append([guy.name, ' - %s' % guy.location.name])
        self.orbit.event([self.user_key], ['WHO', wholist])
        
    def look_room(self):
        room = self.location
        occupantlist = []
        for guy in room.occupants:
            occupantlist.append([guy.name, guy.description])
        itemlist = []
        for item in room.items:
            itemlist.append([item.name, item.description])
        self.orbit.event([self.user_key], ['LOOKROOM', [room.name, room.description, room.directions, occupantlist, itemlist]])
        
    def look_person(self, person):
        self.orbit.event([self.user_key], ['LOOKPERSON', [person.name, person.description, person.attack, person.defense, person.hp]])
        
    def look_item(self, item):
        desc = item.description
        if item.type == 'map':
            desc = item.special
        self.orbit.event([self.user_key], ['LOOKITEM', [item.name, desc, item.type]])
        
    def say_JOIN(self, who, direction):
        self.orbit.event([self.user_key], ['JOINLEAVE', [who.name, ' arrives from ', direction]])
        
    def say_LEAVE(self, who, direction):
        self.orbit.event([self.user_key], ['JOINLEAVE', [who.name, ' goes ', direction]])
        
    def say_PUBLIC(self, who, msg):
        self.orbit.event([self.user_key], ['SAY', [who.name, ' %s' % msg, 'say']])
        
    def say_PRIV(self, who, msg):
        self.orbit.event([self.user_key], ['SAY', [who.name, ' %s' % msg, 'tell']])

    def say_GET(self, who, item):
        if self != who:
            self.orbit.event([self.user_key], ['JOINLEAVE', [who.name, ' picks up ', item.name]])
        else:
            self.orbit.event([self.user_key], ['JOINLEAVE', ['You', ' pick up ', item.name]])
    
    def say_DROP(self, who, item):
        if self != who:
            self.orbit.event([self.user_key], ['JOINLEAVE', [who.name, ' drops ', item.name]])
        else:
            self.orbit.event([self.user_key], ['JOINLEAVE', ['You', ' drop ', item.name]])
                
    def say_ATTACK(self, attacker, target):
        if self == attacker:
            self.orbit.event([self.user_key], ['JOINLEAVE', ['You', ' attack ', target.name]])
        elif self == target:
            self.orbit.event([self.user_key], ['JOINLEAVE', [attacker.name, ' attacks ', 'you!']])
        else:
            self.orbit.event([self.user_key], ['JOINLEAVE', [attacker.name, ' attacks ', target.name]])
    
    def say_GOD(self, person, message1, message2):
        if self == person:
            self.orbit.event([self.user_key], ['GOD', message1])
        else:
            self.orbit.event([self.user_key], ['GOD', message2])
            
    def say_COMBAT(self, roundlist):
        self.orbit.event([self.user_key], ['COMBAT', roundlist])
