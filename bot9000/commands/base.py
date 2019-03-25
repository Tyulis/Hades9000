# -*- coding:utf-8 -*-

import argparse
import discord


class ArgumentError (Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ThrowingArgumentParser (argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentError(message)


class Bot9000Command (object):
    name = NotImplemented
    defaultlang = 'FR'
    minimum_role = 'anyone'

    @classmethod
    def description(cls, language):
        return cls.string('description', language)

    @classmethod
    def help(cls, language):
        return cls.string('help', language)

    @classmethod
    def check(cls, message, arguments, group, player, bot):
        NotImplemented

    @classmethod
    def run(cls, message, arguements, group, player, bot):
        NotImplemented

    @classmethod
    def string(cls, identifier, language):
        if language in cls.strings:
            if identifier in cls.strings[language]:
                return cls.strings[language][identifier]
        if cls.defaultlang in cls.strings:
            if identifier in cls.strings[cls.defaultlang]:
                return cls.strings[cls.defaultlang][identifier]
        return 'Bad string identifier'

    @classmethod
    def make_parser(cls):
        parser = ThrowingArgumentParser()
        for argument in cls.arguments:
            name = argument.strip('?/').split('|')[0]
            optional = '?' in argument
            boolean = '/' in argument
            if '|' in argument:
                short = argument.split('|')[1]
            else:
                short = None
            if optional:
                args = ['-' + name]
            else:
                args = [name]
            if short is not None:
                args.append('-' + short)
            kwargs = {}
            if boolean:
                kwargs['action'] = 'store_true'
            parser.add_argument(*args, **kwargs)
        cls.parser = parser

    strings = {
        'EN': {
            'help': '', 'description': '',
        },
        'FR': {
            'help': '', 'description': '',
        },
    }


class Bot9000PrintCommand (Bot9000Command):
    name = NotImplemented

    @classmethod
    async def run(cls, message, arguments, group, player, bot):
        argsdict = {argument: arguments.__dict__[argument] for argument in arguments.__dict__}
        await bot.send_message(message.channel, cls.string('message', player.language) % argsdict)

    strings = {
        'EN': {
            'help': '', 'description': '', 'message': ''
        },
        'FR': {
            'help': '', 'description': '', 'message': ''
        },
    }
