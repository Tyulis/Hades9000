# -*- coding:utf-8 -*-

import pytz
import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from main.moduledata import _MODULE_DATA
from main.modulestats import *
from ..base import Bot9000Command


class cmd_modinfo (Bot9000Command):
    name = 'modinfo'
    minimum_role = 'anyone'
    arguments = ('module', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            moduleinfo = _MODULE_DATA[arguments.module]
        except KeyError:
            await message.channel.send(cls.string('bad_module', player.language) % arguments.module)
            return
        singles = []
        columns = []
        for info in column_names[player.language].keys():
            if info in ignore_values or moduleinfo[0][info] is None:
                continue
            elif all(map(lambda v: v is None, [level[info] for level in moduleinfo[1:]])) or all([moduleinfo[i][info] == moduleinfo[i + 1][info] for i in range(len(moduleinfo) - 1)]):
                singles.append(info)
            else:
                columns.append(info)
        columns.sort(key=cls.infokey)

        response = cls.string('introduction', player.language) % module_names[player.language][arguments.module]
        for info in singles:
            if info in bool_values:
                response += '**%s**\n' % column_names[player.language][info]
            else:
                response += '**%s** : %s\n' % (column_names[player.language][info], cls.convert(info, moduleinfo[0][info], player.language))
        await message.channel.send(response)

        response = '```'
        table = [[column_names[player.language][info] for info in columns]]
        table.extend([[cls.convert(info, level[info], player.language) for info in columns] for level in moduleinfo])
        sizes = [max([len(level[i]) for level in table]) for i in range(len(table[0]))]
        for row in table:
            response += '|'.join([row[i].rjust(sizes[i]) for i in range(len(row))]) + '\n'
        response += '```'
        await message.channel.send(response)

    @classmethod
    def infokey(cls, colname):
        if colname in column_order:
            return column_order.index(colname)
        else:
            return len(column_order)

    @classmethod
    def convert(cls, info, value, language):
        if info in bool_values:
            return values_translations[language]['_yes' if value else '_no']
        elif value in values_translations[language].keys():
            return values_translations[language][value]
        elif info in time_values:
            days = int(value // (3600*24))
            hours = int(value % (3600*24)) // 3600
            minutes = int(value % 3600) // 60
            seconds = int(value % 60)
            result = ''
            if days != 0:
                result += str(days) + values_translations[language]['_day'] + ' '
            if hours != 0:
                result += str(hours).zfill(2 if len(result) > 0 else 0) + values_translations[language]['_hour'] + ' '
            if minutes != 0:
                result += str(minutes).zfill(2 if len(result) > 0 else 0) + values_translations[language]['_minute'] + ' '
            if seconds != 0:
                result += str(seconds).zfill(2 if len(result) > 0 else 0) + values_translations[language]['_second']
            return result.strip()
        else:
            if isinstance(value, int) or isinstance(value, float):
                result = str(round(value % 1000, 2))
                if value >= 1000:
                    result = str(int((value // 1000) % 1000)) + '\'' + result.zfill(3)
                if value >= 1000000:
                    result = str(int((value // 1000000) % 1000)) + '\'' + result.zfill(7)
                if info in credits_values:
                    result += ' C'
                elif info in hydro_values:
                    result += ' H'
                elif info in percent_values:
                    result += ' %'
                elif info in distance_values:
                    result += ' au'
                return result
            else:
                return str(value)

    strings = {
        'FR': {
            'help': '**$modinfo <module>** : Affiche les informations sur un module. Les identifiants sont donnés par `$techids`',
            'description': 'Affiche les informations sur un module',
            'bad_module': 'Le module "%s" est inconnu. Les identifiants sont donnés par `$techids`',
            'introduction': '__**Informations sur %s**__\n',
        }
    }
