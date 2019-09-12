# -*- coding:utf-8 -*-

import itertools
import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from .account import *
from bot9000.commands import COMMANDS


def corporation(request, corpname, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	try:
		corp = Corporation.objects.get(name=corpname)
	except ObjectDoesNotExist:
		return render(request, 'main/corporation.html', {'title': 'Hades9000 : Corporation %s' % corpname, 'error': 'Cette corporation n\'est pas répertoriée'})
	wslist = WS.objects.filter(corp__id=corp.id)
	data = {
		'title': 'Hades9000 : Corporation %s' % corp.name, 'error': error,
		'corp': corp, 'player': player,
	}
	return render(request, 'main/corporation.html', data)

def editcorp(request, corpname, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	try:
		corp = Corporation.objects.get(name=corpname)
	except ObjectDoesNotExist:
		return corporation(request, player.corp.name, error='Cette corporation n\'existe pas')
	if not player.admin or player.corp.group != corp.group:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	data = {
		'title': 'Hades9000 : Modification de la corporation', 'error': error,
		'corp': corp, 'player': player, 'cmdmodules': COMMANDS, 'groupmodules': corp.group.getcommandmods(),
	}
	return render(request, 'main/editcorp.html', data)

def updatecorp(request, corpname):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	try:
		corp = Corporation.objects.get(name=corpname)
	except ObjectDoesNotExist:
		return corporation(request, player.corp.name, error='Cette corporation n\'existe pas')
	if not player.admin or player.corp.group != corp.group:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	if not request.POST:
		return corporation(request, player.corp.name, error='Requête invalide')
	corp.name = request.POST.get('name')
	corp.relics = int(request.POST.get('relics'))
	if not corp.group.isgroup:
		corp.group.discordlink = request.POST.get('discordlink')
		corp.group.publiclink = 'publiclink' in request.POST
		corp.group.publicmembers = 'publicmembers' in request.POST
		corp.group.publicws = 'publicws' in request.POST
	for member in corp.members():
		member.admin = '%s_admin' % member.id in request.POST
		if '%s_kick' % member.id in request.POST:
			member.corp = None
		member.save()
	cmdmods = []
	for module in COMMANDS.keys():
		if 'cmdmod_%s' % module in request.POST:
			cmdmods.append(module)
	if 'account' not in cmdmods: cmdmods.append('account')
	if 'help' not in cmdmods: cmdmods.append('help')
	if 'hadesstar' not in cmdmods: cmdmods.append('hadesstar')
	corp.group.setcommandmods(cmdmods)
	corp.save()
	corp.group.save()
	if 'save_editgroup' in request.POST:
		return HttpResponseRedirect('/editgroup')
	else:
		return HttpResponseRedirect('/corporation/%s' % player.corp.name)

def integrategroup(request, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	if not player.creator:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	groups = CorpGroup.objects.filter(isgroup=True)
	data = {
		'player': player, 'groups': groups, 'error': error,
	}
	return render(request, 'main/integrategroup.html', data)

def joingroup(request):
	if not request.user.is_authenticated:
		return home(request, error='Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	if not player.creator:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	if not request.POST:
		return corporation(request, player.corp.name, error='Requête invalide')
	groupid = request.POST.get('group')
	try:
		group = CorpGroup.objects.get(id=groupid)
	except ObjectDoesNotExist:
		return integrategroup(request, error='Ce groupe n\'existe pas')
	corp = player.corp
	if not corp.group.isgroup:
		corp.group.delete()
	corp.group = group
	corp.save()
	return HttpResponseRedirect('/group/%s' % group.name)

def creategroup(request):
	if not request.user.is_authenticated:
		return home(request, error='Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	if not player.creator:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	if not request.POST:
		return corporation(request, player.corp.name, error='Requête invalide')
	if request.POST.get('name') in [group.name for group in CorpGroup.objects.all()]:
		return integrategroup(request, error='Un groupe de ce nom existe déjà')
	group = CorpGroup(
		name=request.POST.get('name'),
		discordlink=request.POST.get('discordlink'),
		publicmembers=('publicmembers' in request.POST),
		publiclink=('publiclink' in request.POST),
		publicws=('publicws' in request.POST),
		isgroup=True)
	group.save()
	corp = player.corp
	if not corp.group.isgroup:
		corp.group.delete()
	corp.group = group
	corp.save()
	player.groupcreator = True
	player.groupadmin = True
	player.save()
	return HttpResponseRedirect('/group/%s' % group.name)

def group(request, name, error=None):
	if not request.user.is_authenticated:
		return home(request, error='Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	try:
		group = CorpGroup.objects.get(name=name)
	except ObjectDoesNotExist:
		return corporation(request, player.corp.name, 'Ce groupe n\'existe pas')
	data = {
		'player': player, 'group': group, 'error': error,
	}
	return render(request, 'main/group.html', data)

def editgroup(request, error=None):
	if not request.user.is_authenticated:
		return home(request, error='Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	if not player.admin:
		return corporation(request, player.corp.name, 'Vous n\'avez pas la permission d\'accéder à cette page')
	group = player.corp.group
	if not group.isgroup:
		return HttpResponseRedirect('/editcorp')
	data = {
		'player': player, 'group': group, 'error': error,
		'cmdmodules': COMMANDS, 'groupmodules': group.getcommandmods(),
	}
	return render(request, 'main/editgroup.html', data)


def updategroup(request, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except:
		return home(request, 'Utilisateur invalide')
	if not player.admin:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	if not request.POST:
		return corporation(request, player.corp.name, error='Requête invalide')
	group = player.corp.group
	group.name = request.POST.get('name')
	group.discordlink = request.POST.get('discordlink')
	group.publiclink = 'publiclink' in request.POST
	group.publicmembers = 'publicmembers' in request.POST
	group.publicws = 'publicws' in request.POST
	for member in group.members():
		if '%s_kick' % member.id in request.POST:
			member.corp = None
		member.save()
	cmdmods = []
	for module in COMMANDS.keys():
		if 'cmdmod_%s' % module in request.POST:
			cmdmods.append(module)
	if 'account' not in cmdmods: cmdmods.append('account')
	if 'help' not in cmdmods: cmdmods.append('help')
	if 'hadesstar' not in cmdmods: cmdmods.append('hadesstar')
	group.setcommandmods(cmdmods)
	group.save()
	return HttpResponseRedirect('/group/%s' % group.name)
