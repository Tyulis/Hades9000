# -*- coding:utf-8 -*-

import pytz
import discord
from django.core.exceptions import ObjectDoesNotExist
from main.models import *
from main.moduledata import _MODULE_DATA
from main.modulestats import *
from .base import Bot9000Command

class cmd_question (Bot9000Command):
    name = 'question'
    minimum_role = 'anyone'
    arguments = ('question', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        question = Question()
        question.asker = player
        question.language = player.language
        question.question = arguments.question
        question.save()

        for othergroup in CorpGroup.objects.all():
            if (othergroup.faqnotifs and othergroup.language == question.language) or othergroup == group:
                guild = discord.utils.get(bot.guilds, id=othergroup.discordid)
                channel = discord.utils.get(guild.channels, id=othergroup.faqchannel)
                embed = discord.Embed(
                    title = cls.string('question_title', question.language) % question.id,
                    description = question.question,
                    color = question.asker.corp.group.color,
                )
                embed.set_author(name=player.name, icon_url=message.author.avatar_url)
                await channel.send(embed=embed)
        await message.delete()


    strings = {
        'FR': {
            'help': '**$question <texte>** : Permet de poser une question à la communauté.',
            'description': 'Permet de poser une question à la communauté',
            'question_title': 'Question #%d',
        }
    }

class cmd_answer (Bot9000Command):
    name = 'answer'
    minimum_role = 'anyone'
    arguments = ('questionid', 'answer')
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.questionid.isdigit():
            await message.channel.send(cls.string('not_an_int', player.language))
            return
        questionid = int(arguments.questionid)
        try:
            question = Question.objects.get(id=questionid)
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('bad_quesion_id', player.language)) % questionid
            return
        question = Question.objects.get(id=questionid)
        answers = question.getanswers()
        answer = (player.id, arguments.answer)
        answers.append(answer)
        question.setanswers(answers)
        question.save()

        askguild = discord.utils.get(bot.guilds, id=question.asker.corp.group.discordid)
        channel = discord.utils.get(askguild.channels, id=question.asker.corp.group.faqchannel)
        qembed = discord.Embed(
            title = cls.string('question_title', question.asker.language) % question.id,
            description = question.question,
            color = question.asker.corp.group.color,
        )
        askuser = discord.utils.get(askguild.members, id=question.asker.discordid)
        qembed.set_author(name=question.asker.name, icon_url=askuser.avatar_url)
        await channel.send(embed=qembed)

        for i, answer in enumerate(answers):
            ansplayer = Player.objects.get(id=answer[0])
            ansguild = discord.utils.get(bot.guilds, id=ansplayer.corp.group.discordid)
            aembed = discord.Embed(
                title = cls.string('answer_title', question.asker.language) % (question.id, i),
                description = answer[1],
                color = ansplayer.corp.group.color,
            )
            ansuser = discord.utils.get(ansguild.members, id=ansplayer.discordid)
            aembed.set_author(name=ansplayer.name, icon_url=ansuser.avatar_url)
            await channel.send(embed=aembed)
        await channel.send(askuser.mention)

    strings = {
        'FR': {
            'help': '**$answer <question_id> <réponse>** : Répond à une question posée, en donnant le numéro de la question puis la réponse',
            'description': 'Répond à une question',
            'not_an_int': 'Le numéro de la question doit être un nombre entier',
            'bad_question_id': 'La question n°%d n\'existe pas',
            'question_title': 'Question #%d',
            'answer_title': 'Réponse #%d.%s',
        }
    }


class cmd_qsearch (Bot9000Command):
    name = 'qsearch'
    minimum_role = 'anyone'
    arguments = ('searched', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        fsearched = cls.filter(arguments.searched)
        results = []
        for question in Question.objects.all():
            if arguments.searched.lower() in question.question.lower():
                results.append((1, question))
            elif fsearched in cls.filter(question.question):
                results.append((3, question))
            else:
                for playerid, answer in question.getanswers():
                    if arguments.searched.lower() in answer.lower():
                        results.append((2, question))
                    elif fsearched in cls.filter(answer):
                        results.append((4, question))
        if len(results) == 0:
            await message.channel.send(cls.string('no_result', player.language))
            return

        results.sort()

        for _, question in results:
            askguild = discord.utils.get(bot.guilds, id=question.asker.corp.group.discordid)
            channel = discord.utils.get(askguild.channels, id=question.asker.corp.group.faqchannel)
            qembed = discord.Embed(
                title = cls.string('question_title', player.language) % question.id,
                description = question.question,
                color = question.asker.corp.group.color,
            )
            askuser = discord.utils.get(askguild.members, id=question.asker.discordid)
            qembed.set_author(name=question.asker.name, icon_url=askuser.avatar_url)
            await message.channel.send(embed=qembed)

    @classmethod
    def filter(cls, string):
        string = string.lower().strip()
        string = string.replace('\n', '').replace(' ', '').replace('\t', '')
        string = string.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        string = string.replace('à', 'a').replace('ô', 'o').replace('û', 'u')
        string = string.replace('ç', 'c').replace('î', 'i').replace('ï', 'i')
        return string

    strings = {
        'FR': {
            'help': '**$qsearch <recherche>** : Recherche parmi les questions-réponses',
            'description': 'Recherche parmi les questions-réponses',
            'question_title': 'Question #%d',
            'no_result': 'Pas de résultats',
        }
    }


class cmd_qlook (Bot9000Command):
    name = 'qlook'
    minimum_role = 'anyone'
    arguments = ('id', )
    parser = None

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        if not arguments.id.isdigit():
            await message.channel.send(cls.string('not_an_int', player.language))
            return

        questionid = int(arguments.id)
        try:
            question = Question.objects.get(id=questionid)
        except ObjectDoesNotExist:
            await message.channel.send(cls.string('bad_question_id', player.language) % questionid)
            return

        askguild = discord.utils.get(bot.guilds, id=group.discordid)
        qembed = discord.Embed(
            title = cls.string('question_title', player.language) % question.id,
            description = question.question,
            color = question.asker.corp.group.color,
        )
        askuser = discord.utils.get(askguild.members, id=question.asker.discordid)
        qembed.set_author(name=question.asker.name, icon_url=askuser.avatar_url)
        await message.channel.send(embed=qembed)

        answers = question.getanswers()
        for i, answer in enumerate(answers):
            ansplayer = Player.objects.get(id=answer[0])
            ansguild = discord.utils.get(bot.guilds, id=ansplayer.corp.group.discordid)
            aembed = discord.Embed(
                title = cls.string('answer_title', player.language) % (question.id, i),
                description = answer[1],
                color = ansplayer.corp.group.color,
            )
            ansuser = discord.utils.get(ansguild.members, id=ansplayer.discordid)
            aembed.set_author(name=ansplayer.name, icon_url=ansuser.avatar_url)
            await message.channel.send(embed=aembed)

    strings = {
        'FR': {
            'help': '**$qlook <question_id>** : Affiche une question et ses réponses avec son numéro',
            'description': 'Affiche une question et ses réponses',
            'not_an_int': 'Le numéro de la question doit être un nombre entier',
            'bad_question_id': 'La question n°%d n\'existe pas',
            'question_title': 'Question #%d',
            'answer_title': 'Réponse #%d.%s',
        }
    }
