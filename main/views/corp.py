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

def editcorp(request, error=None):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	try:
		player = Player.objects.get(user__id=request.user.id)
	except ObjectDoesNotExist:
		return home(request, 'Utilisateur invalide')
	if not player.admin:
		return corporation(request, player.corp.name, error='Vous n\'avez pas la permission d\'accéder à cette page')
	data = {
		'title': 'Hades9000 : Modification de la corporation', 'error': error,
		'corp': player.corp, 'player': player,
	}
	return render(request, 'main/editcorp.html', data)

def updatecorp(request):
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
	corp = player.corp
	corp.name = request.POST.get('name')
	corp.relics = int(request.POST.get('relics'))
	corp.group.discordlink = request.POST.get('discordlink')
	corp.group.publiclink = 'publiclink' in request.POST
	corp.group.publicmembers = 'publicmembers' in request.POST
	corp.group.publicws = 'publicws' in request.POST
	for member in corp.members():
		member.admin = '%s_admin' % member.id in request.POST
		if '%s_kick' % member.id in request.POST:
			member.corp = None
		member.save()
		captain = '%s_captain' % member.id in request.POST
		if captain != member.captain():
			update = member.stats()
			update.id = None
			update.date = datetime.datetime.now().astimezone(player.tzinfo())
			update.captain = '%s_captain' % member.id in request.POST
			update.save()
	corp.save()
	corp.group.save()
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
	return 'Nope'

def updategroup(request, error=None):
	return 'Nope'
