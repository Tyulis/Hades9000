# -*- coding:utf-8 -*-

import os
import dotenv
dotenv.load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hades9000.settings')

import django
django.setup()

import discord
from main.models import *
from bot9000.bot import Hades9000Bot

def main(token):
    bot = Hades9000Bot()
    bot.run(token)


if __name__ == '__main__':
    main(os.environ.get('DISCORD_TOKEN'))
