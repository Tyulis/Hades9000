# -*- coding:utf-8 -*-

import pytz
import itertools
import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from main.views.account import *


def dashboard(request, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	user = request.user
	try:
		player = Player.objects.get(user__id=user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	wsmembers = WSPlayer.objects.filter(~Q(ws__state='ws.state.ended'), update__player=player)
	wss = [wsmember.ws for wsmember in wsmembers]
	data = {
		'title': 'Hades9000 : Tableau de bord',
		'player': player, 'wss': wss, 'error': error,
	}
	return render(request, 'main/dashboard.html', data)

def editprofile(request, warnings=[], error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	user = request.user
	try:
		player = Player.objects.get(user__id=user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	available = player.availablemodules()
	maxmodnum = max([len(available[shiptype]) for shiptype in available])
	print(player.orderedships())
	data = {
		'title': 'Hades9000 : Modification du profil', 'error': error, "warnings": warnings,
		'user': user, 'player': player, 'modules': modules, 'modnames': module_names[player.language],
		'maxmodnum': maxmodnum, 'timezones': pytz.common_timezones,
	}
	return render(request, 'main/editprofile.html', data)


def updateprofile(request):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	user = request.user
	try:
		player = Player.objects.get(user__id=user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	if not request.POST:
		return editprofile(request, error='Requête invalide')
	warnings = []
	if 'changecorp' in request.POST:
		player.corp = player.pendingcorp
		player.pendingcorp = None
		roles = player.getpendingroles()
		player.admin = roles[0]
		player.responsible = roles[1]
		player.moderator = roles[2]
		player.setpendingroles([False, False, False])
		player.save()
		return editprofile(request)
	levels = player.shiplevels()
	update = PlayerUpdate.new(player)
	if request.POST.get('password').strip() != '':
		oldpass = request.POST.get('oldpass')
		password = request.POST.get('password')
		passconfirm = request.POST.get('passconfirm')
		if oldpass == '' or password == '' or passconfirm == '':
			warnings.append('Vous devez spécifier l\'ancien mot de passe et confirmer le nouveaupour changer votre mot de passe')
		elif password != passconfirm:
			warnings.append('Le mot de passe et sa confirmation ne correspondent pas')
		elif authenticate(username=user.username, password=oldpass) is None:
			warnings.append('L\'ancien mot de passe est incorrect')
		else:
			user.set_password(password)
			user.save()
			player.confirmed = True
	elif not player.confirmed:
		return editprofile(request, warnings=['Vous devez confirmer votre compte en changeant de mot de passe'])
	player.publicprofile = 'publicprofile' in request.POST
	player.timezone = request.POST.get('timezone')
	player.save()
	update.name = request.POST.get('name')
	update.captain = 'captain' in request.POST
	update.level = request.POST.get('level')
	update.rslevel = request.POST.get('rslevel')
	update.influence = request.POST.get('influence')
	modlevels = {}
	for moduletype in modules:
		for module in modules[moduletype]:
			if not module.endswith('.none'):
				modlevels[module] = int(request.POST.get(module))
	update.setmodules(modlevels)
	update.bslevel = int(request.POST.get('bslevel'))
	update.fslevel = int(request.POST.get('fslevel'))
	update.tslevel = int(request.POST.get('tslevel'))
	# Ships
	ships = []
	for shipid in player.ship_ids():
		if 'ship%d_name' % shipid not in request.POST:
			break
		elif 'ship%d_delete' % shipid in request.POST:
			continue
		ship = {}
		ship['name'] = request.POST.get('ship%d_name' % shipid)
		ship['type'] = request.POST.get('ship%d_type' % shipid)
		ship['id'] = shipid
		for modtype in modules:
			ship[modtype] = []
			for j in itertools.count():
				if 'ship%d_%s%d' % (shipid, modtype, j) not in request.POST:
					break
				ship[modtype].append(request.POST.get('ship%d_%s%d' % (shipid, modtype, j)))
		ships.append(ship)
	if 'addbattleship' in request.POST:
		newtype = 'ship.player.battleship'
	elif 'addminer' in request.POST:
		newtype = 'ship.player.miner'
	elif 'addtransport' in request.POST:
		newtype = 'ship.player.transport'
	else:
		newtype = None
	if newtype is not None:
		ship = {'name': '%s #%d' % (ship_names[player.language][newtype], player.nextshipid), 'id': player.nextshipid, 'type': newtype, 'trade': [], 'mining': [], 'weapon': [], 'shield': [], 'support': []}
		player.nextshipid += 1
		player.save()
		for modtype in player.availablemodules()[newtype]:
			ship[modtype].append('module.%s.none' % modtype)
		ships.append(ship)
	newlevels = update.shiplevels()
	levelchanged = False
	for shiptype in levels:
		level = levels[shiptype]
		newlevel = newlevels[shiptype]
		shipmods = ship_modules[shiptype]
		for modtype in shipmods:
			oldmodnum = shipmods[modtype][level]
			newmodnum = shipmods[modtype][newlevel]
			if newmodnum < oldmodnum:
				levelchanged = True
				for ship in ships:
					if ship['type'] == shiptype:
						ship[modtype] = ship[modtype][:newmodnum]
			elif newmodnum > oldmodnum:
				levelchanged = True
				for ship in ships:
					if ship['type'] == shiptype:
						ship[modtype] += ['module.%s.none' % modtype for i in range(newmodnum - oldmodnum)]
	print(ships)
	update.setships(ships)
	update.save()
	if len(warnings) > 0:
		return editprofile(request, warnings=warnings)
	elif newtype is not None or levelchanged:
		return editprofile(request)
	else:
		return HttpResponseRedirect('/user/%s' % player.name)

def profile(request, username, update=None, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	try:
		user = Player.objects.get(name=username)
	except ObjectDoesNotExist:
		return render(request, 'main/profile.html', {'title': 'Hades9000 : Profil de %s' % username, 'error': 'Cet utilisateur n\'existe pas'})
	if not player.confirmed:
		return waiting_userconfirm(request)
	if update is not None:
		update = datetime.datetime.strptime(update, '%d%m%Y-%H%M').astimezone(player.tzinfo())
		stats = user.stats(update)
	else:
		stats = user.stats()
	available = stats.availablemodules()
	maxmodnum = max([len(available[shiptype]) for shiptype in available])
	data = {
		'title': 'Hades9000 : Profil de %s' % user.name, 'error': error,
		'user': user, 'player': player, 'modules': modules, 'modnames': module_names[player.language],
		'maxmodnum': maxmodnum, 'stats': stats,
	}
	return render(request, 'main/profile.html', data)
