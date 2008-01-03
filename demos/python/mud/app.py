from debug import debug
import random
import client_twisted as orbit_client
import mimetypes
import os
import setup
from game import Player
from game import Item
from util import expose
from twisted.internet import reactor
directions = ['north', 'south', 'east', 'west', 'up', 'down']
speed = 3
fightspeed = 1
sixhours = 15
PING_INTERVAL = 3
timeofday = [
    'Dawn breaks',
    'High noon',
    'The sun sets',
    'Midnight',
]

def refresh(statics, name):
    f = open(os.path.join('static', name))
    statics[name] = f.read()
    f.close()

class App(object):
    def __init__(self):
        self.players = {}
        self.rooms, self.bots, self.items = setup.setup_all()
        for bot in self.bots.values():
            if bot.location == None:
                bot.location = random.choice(self.rooms.keys())
            self.rooms[bot.location].join(bot,'into the void')
        for item in self.items.values():
            if item.location in self.rooms:
                self.rooms[item.location].items.append(item)
                item.location = self.rooms[item.location]
            else:
                self.bots[item.location].get(item)
        self.orbit = orbit_client.OrbitClient()
        self.statics = {}
        self.load_statics()
        self.clock = 0
        self.time = 0
        self.fights = []
        self.fighters = []
        reactor.callLater(speed, self.update_clock)

    def ping_reply(self, player):
        debug('\nping\n')
        player.ping_reply()
        debug( '\nping replied\n')
        
    def update_clock(self):
        self.clock += 1
        for bot in self.bots.values():
            if bot not in self.fighters:
                room, person, dir = bot.move(self.clock)
                if room:
                    self.rooms[room].join(person, dir)
                newfight = bot.fight(self.clock)
                if newfight:
                    self.addfight(newfight)
        if not self.clock % fightspeed:
            self.fight()
        if not self.clock % sixhours:
            for player in self.players.values():
                self.god(player, timeofday[self.time])
            self.time += 1
            if self.time == 4:
                self.time = 0
        if not self.clock % PING_INTERVAL:
            for player in self.players.values():
                if player.send_ping():                    
                    self.rmatch(self.players.pop(player.name.lower()))
        reactor.callLater(speed, self.update_clock)
        
    def addfight(self, (a,b)):
        if [a,b] not in self.fights and [b,a] not in self.fights:
            self.fights.append([a,b])
            self.fighters.append(a)
            self.fighters.append(b)
        
    def fight(self):
        for match in self.fights:
            one, two = match
            one.location.combat(one, two)
            if one.hp < 1:
                self.rmatch(one)
                one.die(random.choice(self.rooms.values()))
            if two.hp < 1:
                self.rmatch(two)
                two.die(random.choice(self.rooms.values()))

    def rmatch(self, var):
        for match in self.fights:
            if var in match:
                a, b = match
                self.fighters.remove(a)
                self.fighters.remove(b)
                self.fights.remove(match)
                
    def load_statics(self):
        for name in [ i for i in os.listdir('static') if not i.startswith('.') ]:
            f = open(os.path.join('static', name))
            self.statics[name] = f.read()
            f.close()
        
    def dispatch(self, request):
        if request.url.startswith('/static/'):
            return self.static(request)
        if hasattr(self, request.url[1:]):
            f = getattr(self, request.url[1:])
            if hasattr(f, 'exposed'):
                try:
                    return f(request)
                except Exception, e:
                    self.error(request, e, f)
            else:
                return self.forbidden(request)
        else:
            return self.not_found(request)

    def static(self, request):
        name = request.url[8:]
        if name not in self.statics:
            return self.not_found(request)
        refresh(self.statics, name)
        request.response.add_header('Content-type', mimetypes.guess_type(name)[0])
        request.response.write(self.statics[name])
        request.response.send()
            
    def error(self, request, e, func):
        request.response.write("An error occured in <b>%s</b>: %s" % (func.func_name, e))
        request.response.send()
        
    def forbidden(self, request):
        request.response.write('FORBIDDEN')
        request.response.send()
    
    def not_found(self, request):
        request.response.write('FILE NOT FOUND')
        request.response.send()
    
    def send_intro(self, player):
#        self.orbit.event([player.user_key], '<script>document.domain="localhost.com"</script>', False)
        self.rooms['the classroom'].join(player,'into the void')
    
    def connect(self, request):
        user = request.form['user']
        if user in self.players:
            request.response.write('you are already connected/connecting')
            request.response.send()
            return
        user_key = '%s, 0, /game' % user
        self.players[user.lower()] = Player(user,user_key,self.orbit)
        reactor.callLater(1, self.send_intro, self.players[user.lower()])
        request.response.write("connecting...")
        request.response.send()
    connect.exposed = True
    
    def msg(self, request):
        debug( '\nmessage\n')
        user = request.form['user']
        msg = request.form['msg'].replace('%20',' ').replace('%22','"').replace('%60','`')
        rawmsg = msg
        if user not in self.players:
            request.response.write('User <b>%s</b> is not connected. Click <a href="/connect?user=%s">here</a> to connect.' % (user, user))
            return request.response.send()
        player = self.players[user]
        self.ping_reply(player)
        if msg != 'ping_reply':
            if ' ' in msg:
                command, msg = msg.split(' ',1)
            else:
                command = msg
            command = command.lower()
            if command in directions:
                self.do_direction(player, command)
            else:
                func = getattr(self, 'do_%s' % command, None)
                if func:
                    func(player, msg)
                else:
                    player.location.say(player, rawmsg)
        request.response.write('<b>%s</b>: %s' % (user, msg))
        request.response.send()
        debug( '\nmessage replied\n')
    msg.exposed = True

    def do_action(self, player, command):
        msg = '%s %s' % (player.name, command)
        player.location.action(player, msg)
    
    def do_quit(self, player, command):
        player.die(player.location, False)
    
    def do_eat(self, player, command):
        command = command.lower()
        if command in self.items and self.items[command] in player.items:
            self.god(player, self.items[command].eat())
            random.choice(self.bots).get(self.items[command])
        else:
            self.not_here(player)
    
    def do_kill(self, player, command):
        command = command.lower()
        if command == 'self':
            self.god(player, "But your life is so good...")
        elif command in self.players and self.players[command] in player.location.occupants and self.players[command] != player:
            player.location.attack(player, self.players[command])
            self.addfight([player, self.players[command]])
        elif command in self.bots and self.bots[command] in player.location.occupants:
            player.location.attack(player, self.bots[command])
            self.addfight([player, self.bots[command]])
        else:
            self.not_here(player)
    
    def do_description(self, player, command):
        player.change_description(' %s' % command)
    
    def do_use(self, player, command):
        command = command.lower()
        object, target = command.split(" on ")
        if object in self.items:
            item = self.items[object]
            msg = ''
            if target in self.bots and self.bots[target].location == player.location:
                target = self.bots[target]
                msg, charge = item.use(target)
            elif target in self.players and self.players[target].location == player.location:
                target = self.players[target]
                msg, charge = item.use(target)
            elif target in self.items and (self.items[target].location == player.location or self.items[target].location == player):
                target = self.items[target]
                msg, charge = item.use(target)
            else:
                return self.not_here(player)
            if charge == 1337:
                for p in self.players.values():
                    if p == player:
                        msg2 = 'You win! You have %s' % msg
                    else:
                        msg2 = '%s wins! %s has %s' % (player.name,player.name,msg)
                    self.god(p, ':::GAME OVER:::<br>%s' % msg2)
                    self.orbit.event([p.user_key], ['restart'])
                return self.__init__()
            for p in player.location.occupants:
                msg2 = msg
                if item.type == 'spell':
                    if p == player:
                        msg2 = 'You'+msg.replace('s ',' ',1)+target.name
                    elif p == target:
                        msg2 = player.name+msg+'YOU!'
                    elif isinstance(p, Player):
                        msg2 = player.name+msg+target.name
                    else:
                        continue
                self.god(p, msg2)
            if not isinstance(target, Item) and target.hp < 1:
                self.rmatch(target)
                target.die(random.choice(self.rooms.values()))
            if not charge:
                random.choice(self.bots).get(item)
        else:
            self.not_here(player)
    
    def do_items(self, player, command):
        if player.items:
            player.look_items()
        else:
            self.god(player, "You're not carrying anything")
    
    def do_get(self, player, command):
        command = command.lower()
        if command in self.items and self.items[command].location == player.location:
            player.get(self.items[command])
        else:
            self.not_here(player)

    def do_drop(self, player, command):
        command = command.lower()
        if command in self.items and self.items[command] in player.items:
            player.drop(self.items[command])
        else:
            self.not_here(player)
        
    def do_who(self, player, command):
        temp = dict(self.players)
        temp.update(self.bots)
        player.who(temp)
    
    def do_look(self, player, command):
        command = command.lower()
        if command == 'look':
            player.look_room()
        elif command == 'self':
            player.look_person(player)
        elif command in self.players and self.players[command].location == player.location:
            player.look_person(self.players[command])
        elif command in self.bots and self.bots[command].location == player.location:
            player.look_person(self.bots[command])
        elif command in self.items and (self.items[command].location == player.location or self.items[command].location == player):
            player.look_item(self.items[command])
        else:
            self.not_here(player)
    
    def do_flee(self, player, command):
        self.god(player, 'You try to flee!')
        dir = random.choice(directions)
        if dir.title() in player.location.directions:
            self.rmatch(player)
            self.do_direction(player, dir)
    
    def do_direction(self, player, command):
        if player in self.fighters:
            return self.god(player, "You're fighting!")
        target = getattr(player.location, command)
        if target:
            player.location.leave(player,command)
            self.rooms[target].join(player,command)
        else:
            self.god(player, 'You bump into the wall')
    
    def do_commands(self, player, msg):
        self.god(player, "<div class=bigblock>COMMANDS:<div class=looking>commands<br>north, south, east, west, up, down<br>tell [someone] [message]<br>kill [someone]<br>flee<br>get [something]<br>use [something] on [someone/something]<br>eat [food]<br>items<br>look<br>look self<br>look [someone/something]<br>description [new self description]<br>action [action]<br>who<br>cls<br>quit</div></div>")
        
    def do_cls(self, player, msg):
        self.orbit.event([player.user_key], ['cls'])
        
    def do_tell(self, player, data):
        def tryit():
            if recipient in self.players:
                self.god(player, "You tell <b>%s</b>: %s" % (self.players[recipient].name, msg))
                self.players[recipient].say('PRIV', player, msg)
                return False
            if recipient in self.bots:
                self.god(player, "You tell <b>%s</b>: %s" % (self.bots[recipient].name, msg))
                self.bots[recipient].say('PRIV', player, msg)
                return False
            return True
        again = True
        iteration = 1
        while again == True:
            if iteration == len(data.split(' ')):
                self.not_here(player)
                break
            recipient = data.split(' ', iteration)
            msg = recipient.pop(-1)
            recipient = ' '.join(recipient).lower()
            again = tryit()
            iteration += 1
            
    def not_here(self, player):
        self.god(player, "You don't see anything like that")
        
    def god(self, player, message):
        self.orbit.event([player.user_key], ['GOD', message])
