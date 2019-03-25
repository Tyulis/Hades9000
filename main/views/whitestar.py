# -*- coding:utf-8 -*-

import pytz
import itertools
import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from .account import home
from .corp import corporation


def whitestar(request, wsid, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        ws = None
        error = 'Cette étoile blanche n\'existe pas'
    playerstats = [member.update for member in ws.members()]
    maxmodnums = []
    for stats in playerstats:
        available = stats.availablemodules()
        maxmodnums.append(max([len(available[shiptype]) for shiptype in available]))
    ships = {}
    for member in ws.members():
        playerships = member.update.getships()
        ships[member.update.player.id] = [ship for ship in playerships if ship['id'] in member.getships()]
    if len(ws.members()) > 0:
        dispos = {member.id: member.getdispos() for member in ws.members()}
        days = [ws.start.astimezone(player.tzinfo()) + datetime.timedelta(days=i) for i in range(6)]
        print(dispos)
        sorteddispos = {}
        for day in days:
            daydispos = {}
            for memberid in dispos.keys():
                if day in dispos[memberid]:
                    daydispos[memberid] = dispos[memberid][day]
                else:
                    daydispos[memberid] = 5
            sorteddispos[day] = daydispos
        maxdispos = {day: min(sorteddispos[day].values()) for day in days}
        avgdispos = {}
        for day in days:
            print(day, sorteddispos[day])
            values = [value for value in sorteddispos[day].values() if value != 5]
            if len(values) != 0:
                avgdispos[day] = sum(values) / len(values)
            else:
                avgdispos[day] = 5
        hasmembers = True
        #print(sorteddispos)
        #print(maxdispos)
        #print(avgdispos)
    else:
        maxdispos = None
        avgdispos = None
        days = None
        hasmembers = False
    data = {
        'player': player, 'ws': ws, 'error': error,
        'wsstates': ws_states, 'playerstats': playerstats, 'maxmodnums': maxmodnums,
        'modules': modules, 'modnames': module_names, 'ships': ships,
        'maxdispos': maxdispos, 'avgdispos': avgdispos, 'days': days, 'hasmembers': hasmembers,
    }
    return render(request, 'main/whitestar.html', data)

def createws(request, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    if not player.responsible:
        return corporation(request, player.corp.name, error='Vous devez être responsable pour lancer une ws')
    data = {
        'player': player, 'corp': player.corp, 'error': error,
    }
    return render(request, 'main/createws.html', data)

def addws(request):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    if not player.admin():
        return corporation(request, player.corp.name, error='Vous devez être administrateur de la corpo pour lancer une ws')
    ws = WS(corp=player.corp)
    ws.comment = request.POST.get('comment')
    ws.state = 'ws.state.inscriptions' if 'inscriptions' in request.POST else 'ws.state.future'
    start = request.POST.get('startdate') + '@' + request.POST.get('starttime')
    ws.start = datetime.datetime.strptime(start, '%Y-%m-%d@%H:%M').astimezone(player.tzinfo()) - player.utcoffset()
    ws.end = ws.start + datetime.timedelta(days=5)
    ws.opponentcorp = "<Inconnue>"
    if request.POST.get('name').strip() != '':
        ws.name = request.POST.get('name')
    else:
        ws.name = 'WS du %s' % ws.start
    ws.save()
    return HttpResponseRedirect('/ws/%d' % ws.id)

def editws(request, wsid, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        return corporation(request, player.corp.name, error='Cette WS n\'existe pas')
    if not player.responsible or player.corp.id != ws.corp.id:
        return corporation(request, player.corp.name, error='Vous devez être responsable pour modifier une ws')
    data = {
        'player': player, 'corp': player.corp, 'ws': ws, 'wsstates': ws_states, 'error': error,
    }
    return render(request, 'main/editws.html', data)

def updatews(request, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    if not request.POST:
        return corporation(request, player.corp.name, error='Requête invalide')
    wsid = int(request.POST.get('wsid'))
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        return corporation(request, player.corp.name, error='Cette WS n\'existe pas')
    if not player.responsible or player.corp.id != ws.corp.id:
        return corporation(request, player.corp.name, error='Vous devez être responsable pour modifier une ws')
    ws.name = request.POST.get('name')
    ws.opponentcorp = request.POST.get('opponentcorp')
    start = request.POST.get('startdate') + '@' + request.POST.get('starttime')
    ws.start = datetime.datetime.strptime(start, '%Y-%m-%d@%H:%M').astimezone(player.tzinfo()) - player.utcoffset()
    ws.score = int(request.POST.get('score'))
    ws.opponentscore = int(request.POST.get('opponentscore'))
    ws.state = request.POST.get('status')
    ws.comment = request.POST.get('comment')
    ws.save()
    return HttpResponseRedirect('/ws/%d' % ws.id)

def registerws(request, wsid, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        return corporation(request, player.corp.name, error='Cette WS n\'existe pas')
    memberdata = registeredships = None
    if player.corp.id != ws.corp.id:
        return corporation(request, player.corp.name, error='Vous ne pouvez pas vous inscrire à une WS d\'une autre corporation')
    elif player not in ws.players() and ws.state != 'ws.state.inscriptions':
        return whitestar(request, ws.id, error='Les inscriptions à cette WS sont fermées')
    elif ws.state == 'ws.state.ended':
        return whitestar(request, ws.id, error='Cette WS est terminée, vous ne pouvez plus modifier votre inscription')
    else:
        if player not in ws.players():
            member = WSPlayer(update=player.stats(), ws=ws)
            member.initdispos(ws.start)
            member.save()
        else:
            member = WSPlayer.objects.get(ws__id=ws.id, update__player__id=player.id)
    dispos = {day: dispo for day, dispo in member.getdispos().items()}
    days = sorted(list(dispos.keys()))
    available = player.availablemodules()
    maxmodnum = max([len(available[shiptype]) for shiptype in available])
    data = {
        'player': player, 'ws': ws, 'error': error, 'member': member,
        'modnames': module_names, 'modules': modules,
        'days': days, 'maxmodnum': maxmodnum, 'dispos': dispos,
    }
    return render(request, 'main/registerws.html', data)

def registeredws(request, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    if not request.POST:
        return corporation(request, player.corp.name, 'Requête invalide')
    wsid = int(request.POST.get('wsid'))
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        return corporation(request, player.corp.name, error='Cette WS n\'existe pas')
    if player.corp.id != ws.corp.id:
        return corporation(request, player.corp.name, error='Vous ne pouvez pas vous inscrire à une WS d\'une autre corporation')
    elif player not in ws.players() and ws.state != 'ws.state.inscriptions':
        return whitestar(request, ws.id, error='Les inscriptions à cette WS sont fermées')
    elif ws.state == 'ws.state.ended':
        return whitestar(request, ws.id, 'Cette WS est terminée, vous ne pouvez plus modifier votre inscription')
    elif 'cancel' in request.POST:
        return HttpResponseRedirect('/ws/%d' % wsid)
    try:
        wsplayer = WSPlayer.objects.get(ws__id=ws.id, update__player__id=player.id)
    except ObjectDoesNotExist:
        wsplayer = WSPlayer(update=player.stats(), ws=ws)
        wsplayer.initdispos(ws.start)
        wsplayer.save()
    if 'quit' in request.POST:
        wsplayer.delete()
        return HttpResponseRedirect('/ws/%d' % wsid)
    ships = []
    for ship in player.ships():
        if 'ship%d_register' % ship['id'] in request.POST:
            ships.append(ship['id'])
    wsplayer.setships(ships)
    dispos = {}
    for key in request.POST:
        if key.startswith('dispo_'):
            dt = datetime.datetime.strptime(key, 'dispo_%d-%m-%Y_%H')
            dt = dt.replace(tzinfo=player.tzinfo())
            dispo = int(request.POST.get(key))
            dispos[dt] = dispo
    wsplayer.setdispos(dispos)
    wsplayer.save()
    return HttpResponseRedirect('/ws/%d' % wsid)

def wsmember(request, wsid, username, error=None):
    if not request.user.is_authenticated:
        return home(request, 'Vous devez vous connecter pour accéder au site')
    user = request.user
    try:
        player = Player.objects.get(user__id=user.id)
    except ObjectDoesNotExist:
        return home(request, 'Utilisateur invalide')
    try:
        ws = WS.objects.get(id=wsid)
    except ObjectDoesNotExist:
        return corporation(request, player.corp.name, error='Cette WS n\'existe pas')
    if player.corp.id != ws.corp.id:
        return corporation(request, player.corp.name, error='Vous n\'avez pas accès à cette page')
    try:
        member = WSPlayer.objects.get(ws__id=wsid, update__player__name=username)
    except ObjectDoesNotExist:
        return whitestar(request, ws.id, error='Ce joueur ne fait pas partie de cette WS')
    dispos = {hour.astimezone(member.player().tzinfo()): dispo for hour, dispo in member.getdispos().items()}
    hours = sorted(list(dispos.keys()))
    days = [[]]
    last = hours[0]
    for hour in hours:
        if hour < ws.start:
            last = hour
            continue
        if hour.day > last.day:
            days.append([])
        days[-1].append(hour)
        last = hour
    available = member.update.availablemodules()
    maxmodnum = max([len(available[shiptype]) for shiptype in available])
    data = {
        'player': player, 'ws': ws, 'error': error, 'member': member,
        'modnames': module_names, 'modules': modules,
        'days': days, 'maxmodnum': maxmodnum, 'dispos': dispos,
    }
    return render(request, 'main/wsmember.html', data)
