import json
import pytz
import datetime
from collections import OrderedDict
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from .data import *


class CorpGroup (models.Model):
	name = models.CharField(max_length=150)
	discordlink = models.CharField(max_length=150, null=True)
	discordid = models.IntegerField(null=True)
	publiclink = models.BooleanField(default=True)
	publicws = models.BooleanField(default=True)
	publicmembers = models.BooleanField(default=True)
	isgroup = models.BooleanField(default=False)

	notifications = models.BooleanField(default=False)
	notifchannel = models.IntegerField(null=True)
	managementchannel = models.IntegerField(null=True)
	language = models.CharField(default='FR', max_length=2)

	adminrole = models.IntegerField(null=True)
	resporole = models.IntegerField(null=True)
	modorole = models.IntegerField(null=True)
	memberrole = models.IntegerField(null=True)

	commandmodules = models.TextField(default='["help", "account"]')
	enable_welcome = models.BooleanField(default=False)
	enable_leavenotif = models.BooleanField(default=False)
	private_welcome = models.BooleanField(default=True)
	welcome = models.TextField(default='')

	custom_commands = models.TextField(default='{}')


	def corporations(self):
		return Corporation.objects.filter(group__id=self.id)

	def members(self):
		ladder = reversed(sorted([(player.influence(), player) for player in Player.objects.filter(corp__group__id=self.id)]))
		return [row[1] for row in ladder]

	def admins(self):
		return Player.objects.filter(corp__group__id=self.id, groupadmin=True)

	def wslist(self):
		return WS.objects.filter(corp__group__id=self.id).order_by('-start')

	def getcommandmods(self):
		return json.loads(self.commandmodules)

	def setcommandmods(self, modules):
		self.commandmodules = json.dumps(modules)

	def getcustomcommands(self):
		return json.loads(self.custom_commands)

	def setcustomcommands(self, commands):
		self.custom_commands = json.dumps(commands)

	def __str__(self):
		return 'CorpGroup %s' % self.name

class Corporation (models.Model):
	name = models.CharField(max_length=150)
	relics = models.IntegerField(default=0)
	group = models.ForeignKey(CorpGroup, on_delete=models.SET_NULL, null=True)

	memberrole = models.IntegerField(null=True)
	wsrole = models.IntegerField(null=True)
	leadrole = models.IntegerField(null=True)

	def influence(self):
		result = 0
		leaderboard = [user.influence() for user in self.members()]
		for score in leaderboard[0:10]:
			result += score * 0.5
		for score in leaderboard[10:20]:
			result += score * 0.25
		for score in leaderboard[20:]:
			result += score * 0.1
		return result

	def level(self):
		level = 0
		for threshold in corp_levels:
			if threshold > self.relics:
				return level
			else:
				level += 1

	def members(self):
		ladder = reversed(sorted([(player.influence(), player) for player in Player.objects.filter(corp__id=self.id)]))
		return [row[1] for row in ladder]

	def wslist(self):
		return WS.objects.filter(corp__id=self.id).order_by('-start')

	def discordlink(self):
		return self.group.discordlink

	def discordid(self):
		return self.group.discordid

	def publiclink(self):
		return self.group.publiclink

	def publicmembers(self):
		return self.group.publicws

	def publicws(self):
		return self.group.publicws

	def __str__(self):
		return "Corp. %s" % self.name


class Player (models.Model):
	name = models.CharField(max_length=150)
	discordid = models.IntegerField(default=-1)
	corp = models.ForeignKey(Corporation, on_delete=models.SET_NULL, null=True, related_name='corp')
	pendingcorp = models.ForeignKey(Corporation, on_delete=models.SET_NULL, null=True, default=None)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	publicprofile = models.BooleanField(default=True)
	nextshipid = models.IntegerField(default=0)
	admin = models.BooleanField(default=False)
	responsible = models.BooleanField(default=False)
	moderator = models.BooleanField(default=False)
	timezone = models.CharField(max_length=120, default='UTC')
	language = models.CharField(max_length=2, default='FR')
	confirmed = models.BooleanField(default=False)
	pendingroles = models.TextField(default='[false, false, false]')
	rsready = models.BooleanField(default=False)

	def stats(self, date=None):
		if date is None:
			return PlayerUpdate.objects.filter(player__id=self.id).order_by('-date')[0]
		else:
			try:
				return PlayerUpdate.objects.filter(player__id=self.id, date__lte=date).order_by('-date')[0]
			except IndexError:
				updates = PlayerUpdate.objects.filter(player__id=self.id).order_by('-date')
				return updates[len(updates) - 1]

	def getpendingroles(self):
		return json.loads(self.pendingroles)

	def setpendingroles(self, roles):  # roles = [<admin>, <respo>, <moderator>]
		self.pendingroles = json.dumps(roles)

	def influence(self):
		return self.stats().influence

	def level(self):
		return self.stats().level

	def rslevel(self):
		return self.stats().rslevel

	def bslevel(self):
		return self.stats().bslevel

	def fslevel(self):
		return self.stats().fslevel

	def tslevel(self):
		return self.stats().tslevel

	def captain(self):
		return self.stats().captain

	def shiplevels(self):
		return self.stats().shiplevels()

	def ships(self, type=None):
		return self.stats().getships(type)

	def orderedships(self):
		return self.stats().orderedships()

	def ship_ids(self):
		return self.stats().ship_ids()

	def availablemodules(self):
		return self.stats().availablemodules()

	def getmodules(self):
		return json.loads(self.stats().modules)

	def setmodules(self, modules):
		self.stats().modules = json.dumps(modules)

	def setmodule(self, module, level):
		mods = json.loads(self.stats().modules)
		mods[module] = level
		self.stats().modules = json.dumps(mods)

	def tzinfo(self):
		return pytz.timezone(self.timezone)

	def utcoffset(self):
		tzinfo = pytz.timezone(self.timezone)
		return tzinfo.utcoffset(datetime.datetime.now())

	def in_ws(self):
		for ws in WS.objects.filter(corp__id=self.corp.id, state="ws.state.running"):
			if self in ws.players():
				return True
		return False

	def __str__(self):
		return 'Player %s' % self.name


class WS (models.Model):
	name = models.CharField(max_length=240)
	corp = models.ForeignKey(Corporation, on_delete=models.CASCADE)
	opponentcorp = models.CharField(max_length=120, default='???')
	score = models.IntegerField(default=0)
	opponentscore = models.IntegerField(default=0)
	start = models.DateTimeField()
	comment = models.TextField(default='')
	state = models.CharField(max_length=120, default='ws.state.future')

	def end(self):
		return self.start + datetime.timedelta(days=5)

	def members(self):
		return WSPlayer.objects.filter(ws__id=self.id)

	def players(self):
		return [member.player() for member in self.members()]

	def __str__(self):
		return 'WS %s - %d /vs/ %d - %s' % (self.corp.name, self.score, self.opponentscore, self.opponentcorp)

class PlayerUpdate (models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
	date = models.DateTimeField()
	level = models.IntegerField(default=1)
	modules = models.TextField(default='{}')
	rslevel = models.IntegerField(default=1)
	influence = models.IntegerField(default=0)
	bslevel = models.IntegerField(default=1)
	fslevel = models.IntegerField(default=1)
	tslevel = models.IntegerField(default=1)
	captain = models.BooleanField(default=False)
	ships = models.TextField(default='[]')

	@classmethod
	def new(cls, player):
		last = player.stats()
		if last.date < datetime.datetime.now().astimezone(player.tzinfo()) - datetime.timedelta(hours=1):
			last.id = None
			last.date = datetime.datetime.now().astimezone(player.tzinfo())
			return last
		else:
			return last

	def getmodules(self):
		return json.loads(self.modules)

	def setmodules(self, modules):
		self.modules = json.dumps(modules)

	def setmodule(self, module, level):
		mods = json.loads(self.stats().modules)
		mods[module] = level
		self.modules = json.dumps(mods)

	def initmodules(self):
		modules = {code: 0 for code in all_modules if not code.endswith('.none')}
		self.setmodules(modules)

	def getships(self, type=None):
		if type is None:
			return json.loads(self.ships)
		else:
			return [ship for ship in json.loads(self.ships) if ship['type'] == type]

	def orderedships(self):
		ships = self.getships()
		battleships = [ship for ship in ships if ship['type'] == 'ship.battleship']
		miners = [ship for ship in ships if ship['type'] == 'ship.miner']
		transports = [ship for ship in ships if ship['type'] == 'ship.transport']
		return sorted(battleships, key=lambda t: t['name']) + sorted(miners, key=lambda t: t['name']) + sorted(transports, key=lambda t: t['name'])

	def setships(self, ships):
		self.ships = json.dumps(ships)

	def getship(self, name):
		return json.loads(self.ships)[name]

	def setship(self, name, ship):
		ships = json.loads(self.ships)
		ships['name'] = ship
		self.ships = json.dumps(ships)

	def shiplevels(self):
		return {'ship.battleship': self.bslevel, 'ship.miner': self.fslevel, 'ship.transport': self.tslevel}

	def ship_ids(self):
		return [ship['id'] for ship in self.getships()]

	def availablemodules(self):
		result = {}
		levels = self.shiplevels()
		for shiptype in ship_modules:
			level = levels[shiptype]
			result[shiptype] = (('trade', ) * ship_modules[shiptype]['trade'][level])
			result[shiptype] += (('mining', ) * ship_modules[shiptype]['mining'][level])
			result[shiptype] += (('weapon', ) * ship_modules[shiptype]['weapon'][level])
			result[shiptype] += (('shield', ) * ship_modules[shiptype]['shield'][level])
			result[shiptype] += (('support', ) * ship_modules[shiptype]['support'][level])
		return result

	def techscore(self):
		totalscore = 0
		shiplevels = self.shiplevels()
		for shiptype in ship_names:
			level = shiplevels[shiptype]
			totalscore += ship_score(shiptype, level)

		modulelevels = self.getmodules()
		for modulecode in modulelevels:
			if modulelevels[modulecode] > 0:
				level = modulelevels[modulecode]
				totalscore += module_score(modulecode, level)
		return totalscore

	def wsscore(self):
		wstotalscore = 0
		modulelevels = self.getmodules()
		for modulecode in modulelevels:
			if modulelevels[modulecode] > 0:
				level = modulelevels[modulecode]
				wsscore = moduledata[modulecode][level - 1]['WhiteStarScore']
				if wsscore is not None:
					wstotalscore += wsscore
		return wstotalscore

	def __str__(self):
		if self.player is not None:
			return 'Player %s update from %s' % (self.player.name, str(self.date))
		else:
			return '-'

class WSPlayer (models.Model):
	update = models.ForeignKey(PlayerUpdate, on_delete=models.SET_NULL, null=True)
	ws = models.ForeignKey(WS, on_delete=models.CASCADE)
	ships = models.TextField(default='[]')
	dispos = models.TextField(default='{}')

	def initdispos(self, start, days=6):
		dispos = {}
		for day in range(days):
			dispos[start + datetime.timedelta(days=day)] = 5
		self.setdispos(dispos)

	def player(self):
		if self.update is None:
			return None
		return self.update.player

	def getships(self, type=None):
		if type is None:
			return json.loads(self.ships)
		else:
			return [ship for ship in json.loads(self.ships) if ship['type'] == type]

	def orderedships(self):
		ships = self.getships()
		battleships = [ship for ship in ships if ship['type'] == 'ship.battleship']
		miners = [ship for ship in ships if ship['type'] == 'ship.miner']
		transports = [ship for ship in ships if ship['type'] == 'ship.transport']
		return sorted(battleships, key=lambda t: t['name']) + sorted(miners, key=lambda t: t['name']) + sorted(transports, key=lambda t: t['name'])

	def setships(self, ships):
		self.ships = json.dumps(ships)

	def getdispos(self):
		dic = json.loads(self.dispos)
		result = {datetime.datetime.strptime(key, '%d-%m-%Y_%H').astimezone(self.update.player.tzinfo()): dispo for key, dispo in dic.items()}
		return result

	def setdispos(self, dispos):
		dic = {dt.astimezone(pytz.UTC).strftime('%d-%m-%Y_%H'): dispo for dt, dispo in dispos.items()}
		self.dispos = json.dumps(dic)

	def __str__(self):
		return 'WS Player %s in %s' % (self.player().name, self.ws)


class RedStar (models.Model):
	group = models.ForeignKey(CorpGroup, on_delete=models.CASCADE)
	player1 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player1')
	player2 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player2')
	player3 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player3')
	player4 = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player4')
	level = models.IntegerField(default=1)

	def players(self):
		return [player for player in (self.player1, self.player2, self.player3, self.player4) if player is not None]

	def __str__(self):
		return 'RS%d in %s' % (self.level, self.group.name)


admin.site.register(CorpGroup)
admin.site.register(Corporation)
admin.site.register(Player)
admin.site.register(PlayerUpdate)
admin.site.register(WSPlayer)
admin.site.register(WS)
admin.site.register(RedStar)
