# -*- coding:utf-8 -*-

import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_switch (Bot9000Command):
    name = 'switch'
    minimum_role = 'member'
    arguments = ('corporation', '?user|u')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.user is not None:
            resporole = discord.utils.get(message.server.roles, id=group.resporole)
            user = discord.utils.get(message.server.members, id=player.discordid)
            if user.top_role < resporole:
                await bot.send_message(message.channel, cls.string('permission_denied', player.language))
                return
            discorduser = bot.get_member(arguments.user, message.server)
            if discorduser is None:
                await bot.send_message(message.channel, cls.string('unknown_member', player.language) % arguments.user)
                return
        else:
            discorduser = discord.utils.get(message.server.members, id=player.discordid)
        try:
            corp = Corporation.objects.get(name=arguments.corporation)
            if corp.group != group:
                await bot.send_message(message.channel, cls.string('foreign_corp', player.language) % (arguments.corporation, group.name))
                return
        except ObjectDoesNotExist:
            await bot.send_message(message.channel, cls.string('unknown_corp', player.language) % arguments.corporation)
            return
        try:
            targetplayer = Player.objects.get(discordid=discorduser.id)
        except ObjectDoesNotExist:
            await bot.send_message(message.channel, cls.string('not_member', player.language) % arguments.user)
            return
        if targetplayer.corp.group != group:
            await bot.send_message(message.channel, cls.string('not_member', player.language) % arguments.user)
            return
        elif targetplayer.corp == corp:
            await bot.send_message(message.channel, cls.string('already_in', player.language) % (arguments.user, corp.name))
        oldcorprole = discord.utils.get(message.server.roles, id=targetplayer.corp.memberrole)
        targetplayer.corp = corp
        targetplayer.save()
        corprole = discord.utils.get(message.server.roles, id=corp.memberrole)
        print(oldcorprole, corprole)
        await bot.remove_roles(discorduser, oldcorprole)
        await bot.add_roles(discorduser, corprole)
        await bot.send_message(message.channel, cls.string('done', player.language) % (targetplayer.name, corp.name))

    strings = {
        'FR': {
            'help': '**$switch <corporation> [-u <utilisateur>]** : Change de corporation dans un même groupe. Pour un responsable, vous pouvez ajouter -u <utilisateur> pour switcher un autre utilisateur',
            'description': 'Permet de changer de corporation dans un même groupe',
            'permission_denied': 'Vous n\'avez pas les droits pour effectuer cette action',
            'foreign_corp': 'La corporation %s ne fait pas partie du groupe %s',
            'unknown_corp': 'La corporation %s est inconnue',
            'done': '%s a bien été switché vers la corporation %s',
            'unknown_member': 'L\'utilisateur %s est inconnu',
            'not_member': 'L\'utilisateur %s n\'est pas membre du groupe ou n\'est pas enregistré',
            'already_in': 'L\'utilisateur %s est déjà membre de la corporation %s',
        }
    }


class cmd_corpexclude (Bot9000Command):
    name = 'corpexclude'
    minimum_role = 'responsible'
    arguments = ('user', '?reason|r')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        discorduser = bot.get_member(arguments.user, message.server)
        if discorduser is None:
            await bot.send_message(message.channel, cls.string('unknown_member', player.language) % arguments.user)
            return
        try:
            targetplayer = Player.objects.get(discordid=discorduser.id)
        except ObjectDoesNotExist:
            await bot.send_message(message.channel, cls.string('not_member', player.language) % arguments.user)
            return
        if targetplayer.corp.group != group:
            await bot.send_message(message.channel, cls.string('not_member', player.language) % arguments.user)
            return
        if arguments.reason is not None:
            reason = arguments.reason
        else:
            reason = cls.string('default_reason', player.language)
        adminrole = discord.utils.get(message.server.roles, id=group.adminrole)
        resporole = discord.utils.get(message.server.roles, id=group.resporole)
        modorole = discord.utils.get(message.server.roles, id=group.modorole)
        memberrole = discord.utils.get(message.server.roles, id=group.memberrole)
        corprole = discord.utils.get(message.server.roles, id=targetplayer.corp.memberrole)
        wsrole = discord.utils.get(message.server.roles, id=targetplayer.corp.wsrole)
        leadrole = discord.utils.get(message.server.roles, id=targetplayer.corp.leadrole)
        await bot.remove_roles(discorduser, adminrole, resporole, modorole, memberrole, corprole, wsrole, leadrole)

        targetplayer.corp = None
        targetplayer.save()
        await bot.send_message(message.channel, cls.string('done', player.language) % arguments.user)
        await bot.send_message(discorduser, cls.string('info_dm', targetplayer.language) % (group.name, reason))

    strings = {
        'FR': {
            'help': '**$corpexclude <user>** : Exclut l\'utilisateur de la corporation et du groupe',
            'description': 'Exclus un utilisateur de la corporation',
            'unknown_member': 'L\'utilisateur %s est inconnu',
            'not_member': 'L\'utilisateur %s n\'est pas membre du groupe ou n\'est pas enregistré',
            'default_reason': 'Raison non spécifiée',
            'done': 'L\'utilisateur %s a été exclus du groupe.',
            'info_dm': 'Vous avez été exclus du groupe %s pour la raison suivante : %s',
        }
    }
