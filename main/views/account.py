# -*- coding:utf-8 -*-

import itertools
import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from main.models import *


def home(request, error=None):
	if request.user.is_authenticated and error is None:
		return HttpResponseRedirect('/dashboard')
	else:
		return render(request, 'main/index.html', {'title': 'Hades9000 : Connexion', 'error': error})

def loginpage(request):
	username = request.POST.get('username')
	password = request.POST.get('password')
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		player = Player.objects.get(user__id=user.id)
		if player.confirmed:
			return HttpResponseRedirect('/dashboard')
		else:
			return HttpResponseRedirect('/editprofile')
	else:
		return home(request, 'Identifiants invalides')

def logoutpage(request):
	if not request.user.is_authenticated:
		return home(request, 'Vous devez vous connecter pour accéder au site')
	logout(request)
	return HttpResponseRedirect('/')
