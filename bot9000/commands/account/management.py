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
            resporole = discord.utils.get(message.guild.roles, id=group.resporole)
            user = discord.utils.get(message.guild.members, id=player.discordid)
            if user.top_role < resporole:
                await message.channel.send(cls.string('permission_denied', player.language))
                return
            discorduser = bot.get_member(arguments.user, message.guild)
            if discorduser is None:
                await message.channel.send(cls.string('unknown_member', player.language) % arguments.user)
                return
        else:
            discorduser = discord.utils.get(message.guild.members, id=player.discordid)
        try:
            corp = Corporation.objects.get(name=arguments.corporation)
            if corp.group != group:
                await message.channel.send(cls.string('foreign_corp', player.language) % (arguments.corporation, group.name))
                return
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('unknown_corp', player.language) % arguments.corporation)
            return
        try:
            targetplayer = Player.objects.get(discordid=discorduser.id)
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_member', player.language) % arguments.user)
            return
        if targetplayer.corp.group != group:
            await message.channel.send(cls.string('not_member', player.language) % arguments.user)
            return
        elif targetplayer.corp == corp:
            await message.channel.send(cls.string('already_in', player.language) % (arguments.user, corp.name))
        oldcorprole = discord.utils.get(message.guild.roles, id=targetplayer.corp.memberrole)
        targetplayer.corp = corp
        targetplayer.save()
        corprole = discord.utils.get(message.guild.roles, id=corp.memberrole)
        print(oldcorprole, corprole)
        await discorduser.remove_roles(oldcorprole)
        await discorduser.add_roles(corprole)
        await message.channel.send(cls.string('done', player.language) % (targetplayer.name, corp.name))

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


class cmd_corpkick (Bot9000Command):
    name = 'corpkick'
    minimum_role = 'responsible'
    arguments = ('user', '?reason|r')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        discorduser = bot.get_member(arguments.user, message.guild)
        if discorduser is None:
            await message.channel.send(cls.string('unknown_member', player.language) % arguments.user)
            return
        try:
            targetplayer = Player.objects.get(discordid=discorduser.id)
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('not_member', player.language) % arguments.user)
            return
        if targetplayer.corp.group != group:
            await message.channel.send(cls.string('not_member', player.language) % arguments.user)
            return
        if arguments.reason is not None:
            reason = arguments.reason
        else:
            reason = cls.string('default_reason', player.language)
        adminrole = discord.utils.get(message.guild.roles, id=group.adminrole)
        resporole = discord.utils.get(message.guild.roles, id=group.resporole)
        modorole = discord.utils.get(message.guild.roles, id=group.modorole)
        memberrole = discord.utils.get(message.guild.roles, id=group.memberrole)
        corprole = discord.utils.get(message.guild.roles, id=targetplayer.corp.memberrole)
        wsrole = discord.utils.get(message.guild.roles, id=targetplayer.corp.wsrole)
        leadrole = discord.utils.get(message.guild.roles, id=targetplayer.corp.leadrole)
        await discorduser.remove_roles(adminrole, resporole, modorole, memberrole, corprole, wsrole, leadrole)

        targetplayer.corp = None
        targetplayer.save()
        await message.channel.send(cls.string('done', player.language) % arguments.user)
        await discorduser.send(cls.string('info_dm', targetplayer.language) % (group.name, reason))

    strings = {
        'FR': {
            'help': '**$corpkick <user>** : Exclut l\'utilisateur de la corporation et du groupe',
            'description': 'Exclus un utilisateur de la corporation',
            'unknown_member': 'L\'utilisateur %s est inconnu',
            'not_member': 'L\'utilisateur %s n\'est pas membre du groupe ou n\'est pas enregistré',
            'default_reason': 'Raison non spécifiée',
            'done': 'L\'utilisateur %s a été exclus du groupe.',
            'info_dm': 'Vous avez été exclus du groupe %s pour la raison suivante : %s',
        }
    }


class cmd_setchannel (Bot9000Command):
    name = 'setchannel'
    minimum_role = 'admin'
    arguments = ('identifier', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if group.discordid != None:
            if arguments.identifier == 'notifications':
                group.notifchannel = message.channel.id
                await message.channel.send(cls.string('set_notif_channel', player.language) % message.channel.name)
            elif arguments.identifier == 'management':
                group.managementchannel = message.channel.id
                await message.channel.send(cls.string('set_management_channel', player.language) % message.channel.name)
            else:
                await message.channel.send(cls.string('bad_identifier', player.language) % arguments.identifier)
            group.save()

    strings = {
        'FR':{
            'help': '**$setchannel <id>** : Enregistre le channel pour un usage particulier. <id> peut être "notifications" pour le channel où seront publiées les notifications sur l\'état de Hades9000, "management" pour le channel réservé à l\'administration du serveur',
            'description': 'Spécifie un salon pour certains usages spécifiques',
            'bad_identifier': 'L\'ID "%s" est invalide. L\'argument peut être "notifications" ou "management"',
            'set_notif_channel': 'Le channel %s sera utilisé pour envoyer les notifications relatives à l\'état de Hades9000 et les messages de bienvenue',
            'set_management_channel': 'Le channel %s sera utilisé pour les messages relatifs à l\'administration du serveur et de Hades9000',
        }
    }

class cmd_setrole (Bot9000Command):
    name = 'setrole'
    minimum_role = 'admin'
    arguments = ('identifier', 'name')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        role = discord.utils.get(message.guild.roles, name=arguments.name)
        if role is None:
            await message.channel.send(cls.string('bad_role', player.language) % arguments.name)
            return
        if arguments.identifier == 'admin':
            group.adminrole = role.id
        elif arguments.identifier == 'responsible':
            group.resporole = role.id
        elif arguments.identifier == 'moderator':
            group.modorole = role.id
        elif arguments.identifier == 'member':
            group.memberrole = role.id
        elif arguments.identifier == 'rs1':
            group.rs1role = role.id
        elif arguments.identifier == 'rs2':
            group.rs2role = role.id
        elif arguments.identifier == 'rs3':
            group.rs3role = role.id
        elif arguments.identifier == 'rs4':
            group.rs4role = role.id
        elif arguments.identifier == 'rs5':
            group.rs5role = role.id
        elif arguments.identifier == 'rs6':
            group.rs6role = role.id
        elif arguments.identifier == 'rs7':
            group.rs7role = role.id
        elif arguments.identifier == 'rs8':
            group.rs8role = role.id
        elif arguments.identifier == 'rs9':
            group.rs9role = role.id
        elif arguments.identifier == 'rs10':
            group.rs10role = role.id
        elif ':' in arguments.identifier:
            corpname, cidentifier = arguments.identifier.split(':')
            try:
                corp = Corporation.objects.get(group__id=group.id, name=corpname)
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('bad_corp', payer.language) % corpname)
                return
            if cidentifier == 'member':
                corp.memberrole = role.id
            elif cidentifier == 'ws1':
                corp.ws1role = role.id
            elif cidentifier == 'lead1':
                corp.lead1role = role.id
            elif cidentifier == 'ws2':
                corp.lead2role = role.id
            elif cidentifier == 'lead2':
                corp.ws2role = role.id
            else:
                await message.channel.send(cls.string('bad_identifier', player.language) % arguments.identifier)
                return
            corp.save()
        else:
            await message.channel.send(cls.string('bad_identifier', player.language) % arguments.identifier)
            return
        await message.channel.send(cls.string('done', player.language) % (arguments.name, arguments.identifier))
        group.save()

    strings = {
        'FR': {
            'help': '**$setrole <identifier> <role-name>** : Change un rôle utilisé par Hades9000. L\'identifiant peut être "admin", "responsible", "moderator", "member", "rs1", "rs2", ... Pour changer un rôle de corporation, l\'identifiant doit être "<nom de la corpo>:member", "<nom de la corpo>:ws", "<nom de la corpo>:lead"',
            'description': 'Change un rôle utilisé par Hades9000',
            'bad_role': 'Le rôle %s n\'existe pas',
            'bad_identifier': 'L\'identifiant de rôle %s n\'existe pas, lisez l\'aide de la commande pour plus d\'informations',
            'bad_corp': 'La corporation %s n\'existe pas dans ce groupe',
            'done': 'Le rôle %s a bien été affecté à %s',
        }
    }

class cmd_usedroles (Bot9000Command):
    name = 'usedroles'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        norole = cls.string('none', player.language)

        role = discord.utils.get(message.guild.roles, id=group.adminrole)
        name = (role.name if role is not None else norole)
        response = cls.string('adminrole', player.language) % name

        role = discord.utils.get(message.guild.roles, id=group.resporole)
        name = (role.name if role is not None else norole)
        response += cls.string('resporole', player.language) % name

        role = discord.utils.get(message.guild.roles, id=group.modorole)
        name = (role.name if role is not None else norole)
        response += cls.string('modorole', player.language) % name

        role = discord.utils.get(message.guild.roles, id=group.memberrole)
        name = (role.name if role is not None else norole)
        response += (cls.string('memberrole', player.language) % name) + '\n'

        for i, roleid in enumerate(group.rsroles()):
            role = discord.utils.get(message.guild.roles, id=roleid)
            name = (role.name if role is not None else norole)
            response += cls.string('rsrole', player.language) % (i + 1, i + 1, name)
        response += '\n'

        for corp in group.corporations():
            role = discord.utils.get(message.guild.roles, id=corp.memberrole)
            name = (role.name if role is not None else norole)
            response += cls.string('corpmember', player.language) % (corp.name, corp.name, name)

            role = discord.utils.get(message.guild.roles, id=corp.ws1role)
            name = (role.name if role is not None else norole)
            response += cls.string('corpws1', player.language) % (corp.name, corp.name, name)

            role = discord.utils.get(message.guild.roles, id=corp.lead1role)
            name = (role.name if role is not None else norole)
            response += cls.string('corplead1', player.language) % (corp.name, corp.name, name)

            role = discord.utils.get(message.guild.roles, id=corp.ws2role)
            name = (role.name if role is not None else norole)
            response += cls.string('corpws2', player.language) % (corp.name, corp.name, name)

            role = discord.utils.get(message.guild.roles, id=corp.lead2role)
            name = (role.name if role is not None else norole)
            response += cls.string('corplead2', player.language) % (corp.name, corp.name, name) + '\n'
        await message.channel.send(response)

    strings = {
        'FR': {
            'help': '**$usedroles** : Liste les rôles utilisés par Hades9000 sur ce serveur',
            'description': 'Liste les rôles utilisés par Hades9000 sur ce serveur',
            'none': '*<aucun>*',
            'adminrole': '__Administrateur__ *[admin]* : **%s**\n',
            'resporole': '__Responsable__ *[responsible]* : **%s**\n',
            'modorole': '__Modérateur__ *[moderator]* : **%s**\n',
            'memberrole': '__Membre__ *[member]* : **%s**\n',
            'rsrole': '__RS%d__ *[rs%d]* : **%s**\n',
            'corpmember': '__Membre %s__ *[%s:member]* : **%s**\n',
            'corpws1': '__%s WS 1__ *[%s:ws1]* : **%s**\n',
            'corplead1': '__Capitaine WS 1 %s__ *[%s:lead1]* : **%s**\n',
            'corpws2': '__%s WS 2__ *[%s:ws2]* : **%s**\n',
            'corplead2': '__Capitaine WS 2 %s__ *[%s:lead2]* : **%s**\n',
        }
    }

class cmd_togglemodule (Bot9000Command):
    name = 'togglemodule'
    minimum_role = 'admin'
    arguments = ('module', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        allmods = bot.command_modules()
        if arguments.module not in allmods:
            await message.channel.send(cls.string('bad_module', player.language) % arguments.module)
            return
        if allmods[arguments.module]['__mandatory']:
            await message.channel.send(cls.string('mandatory', player.language) % arguments.module)
            return
        modules = group.getcommandmods()
        if arguments.module in modules:
            modules.remove(arguments.module)
            activated = False
        else:
            modules.append(arguments.module)
            activated = True
        group.setcommandmods(modules)
        group.save()
        if activated:
            await message.channel.send(cls.string('activated', player.language) % arguments.module)
        else:
            await message.channel.send(cls.string('desactivated', player.language) % arguments.module)

    strings = {
        'FR': {
            'help': '**$togglemodule <module>** : Active ou désactive un module de commandes pour ce serveur. Les modules activables sont `whitestar`, `redstar`, `management` et `utilities`',
            'description': 'Permet d\'activer et désactiver des modules de commandes pour ce serveur',
            'bad_module': 'Le module *%s* n\'existe pas',
            'mandatory': 'Le module *%s* est obligatoire pour le bon fonctionnement de Hades9000, vous ne pouvez pas le désactiver',
            'activated': 'Le module *%s* a été activé',
            'desactivated': 'Le module *%s* a été désactivé',
        }
    }

class cmd_groupinfo (Bot9000Command):
    name = 'groupinfo'
    minimum_role = 'member'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        response = cls.string('introduction', player.language) % group.name
        response += cls.string('membercorps', player.language) % ', '.join([corp.name for corp in group.corporations()])
        response += cls.string('invitation', player.language) % group.discordlink
        response += cls.string('discordid', player.language) % group.discordid
        response += cls.string('modules', player.language) % ', '.join(group.getcommandmods())
        notifchannel = discord.utils.get(message.guild.channels, id=group.notifchannel)
        if notifchannel is not None:
            response += cls.string('notifchannel', player.language) % (notifchannel.mention, cls.string('activated' if group.notifications else 'desactivated', player.language))
        else:
            response += cls.string('no_notifchannel', player.language)
        managementchannel = discord.utils.get(message.guild.channels, id=group.managementchannel)
        if managementchannel is not None:
            response += cls.string('managementchannel', player.language) % managementchannel.mention
        else:
            response += cls.string('no_managementchannel', player.language)
        custom = gorup.getcustomcommands()
        if len(custom) > 0:
            response += cls.string('customcommands', player.language) % ', '.join(custom.keys())
        else:
            response += cls.string('no_customcommands', player.language)
        await message.channel.send(response)

    strings = {
        'FR': {
            'help': '**$groupinfo** : Affiche les informations sur le groupe',
            'description': 'Affiche les informations sur le groupe',
            'introduction': '**__Informations sur le groupe *%s*__**\n',
            'membercorps': '__Corporations membres__ : %s\n',
            'invitation': '__Invitation__ : %s\n',
            'discordid': '__ID Discord__ : %d\n',
            'modules': '__Modules actifs__ : %s\n',
            'notifchannel': '__Salon des notifications__ : %s *(%s)*\n',
            'no_notifchannel': '*Pas de salon pour les notifications*\n',
            'activated': 'activé',
            'desactivated': 'désactivé',
            'managementchannel': '__Salon d\'administration__ : %s\n',
            'no_managementchannel': '*Pas de salon d\'administration*\n',
            'customcommands': '__Commandes custom__ : %s\n',
            'no_customcommands': '*Pas de commandes custom*\n',
        }
    }

class cmd_corpinfo (Bot9000Command):
    name = 'corpinfo'
    minimum_role = 'member'
    arguments = ('?corp|c', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not group.isgroup:
            corp = group.corporations()[0]
        elif arguments.corp is None:
            corp = player.corp
        else:
            try:
                corp = Corporation.objects.get(group=group, name=arguments.corp)
            except ObjectDoesNotExist:
                await message.channel.send(cls.string('bad_corp', player.language) % arguments.corp)
                return
        response = cls.string('introduction', player.language) % corp.name
        response += cls.string('influence', player.language) % corp.influence()
        response += cls.string('relics', player.language) % corp.relics
        response += cls.string('members', player.language) % '\n'.join([member.name for member in corp.members()])
        await message.channel.send(response)

    strings = {
        'FR': {
            'help': '**$corpinfo [-c <corporation>]** : Affiche les informations sur la corporation. L\'option -c <corporation> est nécessaire pour désigner une corporation seulement dans un groupe de corporations',
            'description': 'Affiche les informations sur une corporation',
            'bad_corp': 'La corporation %s n\'existe pas dans ce groupe',
            'introduction': '**__Informations sur *%s*__**\n',
            'influence': '__Influence__ : %d\n',
            'relics': '__Reliques__ : %d\n',
            'members': '__Membres__ :\n%s\n\n',
        }
    }

class cmd_update (Bot9000Command):
    name = 'update'
    minimum_role = 'admin'
    arguments = ()
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        bot.setup_group(group)
        await message.channel.send(cls.string('done', player.language))

    strings = {
        'FR': {
            'help': '**$update** : Met à jour les informations du groupe',
            'description': 'Met à jour les informations du groupe',
            'done': 'Les informations ont été rechargées',
        }
    }
