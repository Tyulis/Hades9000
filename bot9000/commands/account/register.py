# -*- coding:utf-8 -*-

import random
import datetime
import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from ..base import Bot9000Command


class cmd_setupgroup (Bot9000Command):
    name = 'setupgroup'
    minimum_role = 'admin'
    arguments = ('name', 'language', 'role_admin', 'role_responsible', 'role_moderator', 'role_member')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if group.discordid is None:
            try:
                CorpGroup.objects.get(name=arguments.name)
                await message.channel.send(cls.string('name_already_used', language) % arguments.name)
                return
            except ObjectDoesNotExist:
                pass
            group = CorpGroup(name=arguments.name, language=arguments.language, discordid=message.guild.id, isgroup=True)
        group.faqcolor = random.randint(0x000000, 0xFFFFFF)
        adminrole = discord.utils.get(message.guild.roles, name=arguments.role_admin)
        if adminrole is None:
            await message.channel.send(cls.string('bad_role', arguments.language) % arguments.role_admin)
            return
        resporole = discord.utils.get(message.guild.roles, name=arguments.role_responsible)
        if resporole is None:
            await message.channel.send(cls.string('bad_role', arguments.language) % arguments.role_responsible)
            return
        modorole = discord.utils.get(message.guild.roles, name=arguments.role_moderator)
        if modorole is None:
            await message.channel.send(cls.string('bad_role', arguments.language) % arguments.role_moderator)
            return
        memberrole = discord.utils.get(message.guild.roles, name=arguments.role_member)
        if memberrole is None:
            await message.channel.send(cls.string('bad_role', arguments.language) % arguments.role_member)
            return
        group.adminrole = adminrole.id
        group.resporole = resporole.id
        group.modorole = modorole.id
        group.memberrole = memberrole.id
        group.save()
        corps = Corporation.objects.filter(group__discordid=message.guild.id)
        for corp in corps:
            corp.group = group
            corp.save()
            await message.channel.send(cls.string('corp_joined', arguments.language) % corp.name)
        await message.channel.send(cls.string('done', arguments.language) % group.name)


    strings = {
        'FR': {
            'help': '**$setupgroup <nom> <langue> <role_admin> <role_responsible> <role_moderator> <role_member>** : Enregistre ce serveur discord comme étant celui du group <nom>, et utilise la langue sélectionnée (code langage à 2 caractères, comme "FR" ou "EN"). Précisez les noms des rôles généraux comme indiqué, admin, responsable, modérateur et membres',
            'description': 'Enregistrement du groupe',
            'name_already_used': 'Le groupe %s existe déjà',
            'bad_role': 'Le rôle %s n\'existe pas sur ce serveur',
            'corp_joined': 'La corporation %s a été ajoutée au groupe',
            'done': 'Le groupe % a bien été créé !'
        }
    }


class cmd_setupcorp (Bot9000Command):
    name = 'setupcorp'
    minimum_role = 'admin'
    arguments = ('name', 'role_member', 'role_ws', 'role_lead', '?role_admin|a', '?role_responsible|r', '?role_moderator|m', '?language|l')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        try:
            corp = Corporation.objects.get(name=arguments.name)
            if corp.group != group:
                await message.channel.send(cls.string('name_already_used', group.language) % arguments.name)
                return
        except ObjectDoesNotExist:
            corp = Corporation(name=arguments.name)
        if group.discordid is not None:
            corp.group = group
            if group.isgroup and (arguments.role_admin is not None or arguments.role_responsible is not None or arguments.role_moderator is not None):
                await message.channel.send(cls.string('defaulting_group', language))
        else:
            group.faqcolor = random.randint(0x000000, 0xFFFFFF)
            if arguments.language is not None:
                group = CorpGroup(name=arguments.name, language=arguments.language, discordid=message.guild.id, isgroup=False)
            else:
                group = CorpGroup(name=arguments.name, language='FR', discordid=discord.guild.id, isgroup=False)
            adminrole = discord.utils.get(message.guild.roles, name=arguments.role_admin)
            if adminrole is None:
                await message.channel.send(cls.string('bad_role', group.language) % arguments.role_admin)
                return
            resporole = discord.utils.get(message.guild.roles, name=arguments.role_responsible)
            if resporole is None:
                await message.channel.send(cls.string('bad_role', group.language) % arguments.role_responsible)
                return
            modorole = discord.utils.get(message.guild.roles, name=arguments.role_moderator)
            if modorole is None:
                await message.channel.send(cls.string('bad_role', group.language) % arguments.role_moderator)
                return
            memberrole = discord.utils.get(message.guild.roles, name=arguments.role_member)
            if memberrole is None:
                await message.channel.send(cls.string('bad_role', group.language) % arguments.role_member)
                return
            group.adminrole = adminrole.id
            group.resporole = adminrole.id
            group.modorole = modorole.id
            group.memberrole = memberrole.id
            group.save()
            corp.group = group
        corprole = discord.utils.get(message.guild.roles, name=arguments.role_member)
        if corprole is None:
            await message.channel.send(cls.string('bad_role', group.language) % arguments.role_member)
            return
        wsrole = discord.utils.get(message.guild.roles, name=arguments.role_ws)
        if wsrole is None:
            await message.channel.send(cls.string('bad_role', group.language) % arguments.role_ws)
            return
        leadrole = discord.utils.get(message.guild.roles, name=arguments.role_lead)
        if leadrole is None:
            await message.channel.send(cls.string('bad_role', group.language) % arguments.role_lead)
            return
        corp.memberrole = corprole.id
        corp.ws1role = wsrole.id
        corp.lead1role = leadrole.id
        corp.save()
        await message.channel.send(cls.string('done', group.language) % corp.name)


    strings = {
        'FR': {
            'help': '**$setupcorp <nom> <role_member> <role_ws1> <role_lead1> [-a <role_admin>] [-r <role_responsible>] [-m <role_moderator>] [-l <langue>]** : Enregistre ce serveur discord pour la corporation <nom>. S\'il n\'y a pas de groupe sur ce discord, utilisera la langue sélectionnée (code langage à 2 caractères, comme "FR" ou "EN"). Vous devez entrer les rôles de membre de la corporation, joueur de WS 1 et capitaine de WS 1 de cette corpo. Les autres rôles sont à préciser si la corporation ne fait pas partie d\'un groupe. Les rôles possibles sont par la suite affichés par `$usedroles` et modifiables avec `$setrole`',
            'description': 'Enregistrement de la corporation',
            'name_already_used': 'La corporation %s existe déjà',
            'defaulting_group': 'Les rôles de base (admin, responsable, modérateur, membre) ont été ignorés. Modifiez ceux du groupe à la place.',
            'bad_role': 'Le rôle %s n\'existe pas sur ce serveur',
            'done': 'La corporation %s a bien été créée !',
        }
    }

class cmd_register (Bot9000Command):
    name = 'register'
    minimum_role = 'responsible'
    arguments = ('name', '?pseudo|p', '?language|l', '?corporation|c', '?/new|n')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if arguments.language is not None:
            language = arguments.language
        else:
            language = group.language
        if arguments.corporation is not None:
            corpname = arguments.corporation
        else:
            if not group.isgroup:
                corpname = group.corporations()[0].name
            else:
                await message.channel.send(cls.string('choose_corp', language))
                return

        discorduser = bot.get_member(arguments.name, message.guild)
        if discorduser is None:
            await message.channel.send(cls.string('username_not_found', language) % arguments.name)
            return
        username = arguments.name
        if arguments.pseudo is not None:
            username = arguments.pseudo
            await discorduser.edit(nick=arguments.pseudo)
        try:
            corp = Corporation.objects.get(name=corpname)
            if corp.group != group:
                await message.channel.send(cls.string('foreign_corp', language) % corpname)
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_corp', language) % corpname)
            return

        adminrole = discord.utils.get(message.guild.roles, id=group.adminrole)
        resporole = discord.utils.get(message.guild.roles, id=group.resporole)
        modorole = discord.utils.get(message.guild.roles, id=group.modorole)
        memberrole = discord.utils.get(message.guild.roles, id=group.memberrole)
        corprole = discord.utils.get(message.guild.roles, id=corp.memberrole)
        await discorduser.add_roles(memberrole, corprole)
        try:
            player = Player.objects.get(name=username)
            if not arguments.new and discorduser.id != player.discordid:
                await message.channel.send(cls.string('pseudo_already_taken', player.language) % username)
                return
            player.pendingcorp = corp
            roles = [discorduser.top_role >= adminrole, discorduser.top_role >= resporole, discorduser.top_role >= modorole]
            player.setpendingroles(roles)
            player.save()
            if player.corp is not None:
                if player.corp.group == corp.group:
                    oldcorprole = discord.utils.get(message.guild.roles, id=player.corp.memberrole)
                    await discorduser.remove_roles(oldcorprole)
                    await message.channel.send(cls.string('replace_switch', language) % (corp.name, username))
            await discorduser.send(cls.string('instructions_move', language) % (username, corp.name, bot.make_url('editprofile')))
            await message.channel.send(cls.string('confirm_move', language) % (username, corp.name, discorduser.mention))
        except ObjectDoesNotExist:
            password = bot.generate_temp_password()
            user = User.objects.create_user(username=username, password=password)
            user.save()
            player = Player(name=username, language=language, corp=corp, user=user, discordid=discorduser.id)
            if discorduser.top_role >= modorole:
                player.moderator = True
            if discorduser.top_role >= resporole:
                player.responsible = True
            if discorduser.top_role >= adminrole:
                player.admin = True
            player.save()
            update = PlayerUpdate(date=datetime.datetime.now(), player=player)
            update.initmodules()
            update.save()
            await discorduser.send(cls.string('instructions_create', language) % (username, corp.name, bot.make_url(''), username, password))
            await message.channel.send(cls.string('confirm_create', language) % (username, discorduser.mention))

    strings = {
        'FR': {
            'help': '**$register <nom> [-p <pseudo>] [-l <langue>] [-c <corporation>] [-n]**: Enregistre l\'utilisateur avec le nom discord donné, et si défini, lui donne le <pseudo> et le <language> donnés. Si -n est précisé, force la création d\'un nouvel utilisateur, à n\'utiliser qu\'en confirmation, pas directement. Si c\'est le discord d\'un groupe, utiliser -c <corporation> pour spécifier la corporation',
            'description' : 'Inscrit un utilisateur dans le groupe',
            'pseudo_already_taken': 'Le pseudo %s est déjà pris. Confirmez-vous que vous parlez bien cet utilisateur ? Si oui, refaites cette comande avec l\'option -n. Sinon, choisissez un autre pseudo avec l\'option -p <pseudo>',
            'choose_corp': 'Ceci est le discord d\'un groupe de corporations. Vous devez choisir la corporation avec l\'option -c <corporation>',
            'unknown_corp': 'La corporation %s est inconnue',
            'foreign_corp': 'La corporation %s n\'est pas définie sur ce serveur',
            'replace_switch': '*`$register` fonctionne aussi, mais notez que comme les deux corporations font partie du même groupe, `$switch %s -u %s` permet d\'effectuer cette action plus simplement et rapidement*',
            'username_not_found': 'Le nom d\'utilisateur %s n\'a pas été trouvé sur ce serveur. Assurez-vous que le joueur est bien sur ce serveur, et qu\'il s\'agit bien de son nom d\'utilisateur ou de son surnom sur ce serveur',
            'confirm_create': 'Le compte de %s a été créé. %s, suivez les instructions envoyées en message privé pour confirmer votre compte.',
            'instructions_create': '%s, votre compte a été créé dans la corporation %s, bienvenue dans le bel univers de Hades9000 ! Pour confirmer votre compte et renseigner vos informations, visitez %s et connectez vous avec votre pseudo `%s` et le mot de passe provisoire `%s`. Vous devrez obligatoirement changer ce mot de passe pour continuer. Bon jeu ^^',
            'confirm_move': 'Le compte de %s est en déplacement dans la corporation %s. %s, connectez-vous sur votre compte pour confirmer le déplacement',
            'instructions_move': '%s, votre compte a été déplacé vers la corporation %s. Pour confirmer ce changement, visitez %s (vous pouvez aussi passer par les menus Profil > Modifier).',
        }
    }
