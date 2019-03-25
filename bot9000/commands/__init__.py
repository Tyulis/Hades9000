# -*- coding:utf-8 -*-

from .help import *
from .account import *
from .hadesstar import *


COMMANDS = {
    'help': {
        cmd_help.name: cmd_help,
        cmd_sitelink.name: cmd_sitelink,
        cmd_hello.name: cmd_hello,
        '__mandatory': True,
    },
    'account': {
        cmd_setupgroup.name: cmd_setupgroup,
        cmd_setupcorp.name: cmd_setupcorp,
        cmd_register.name: cmd_register,
        cmd_switch.name: cmd_switch,
        cmd_corpexclude.name: cmd_corpexclude,
        '__mandatory': True,
    },
    'hadesstar': {
        cmd_playerinfo.name: cmd_playerinfo,
        cmd_setinfo.name: cmd_setinfo,
        cmd_techs.name: cmd_techs,
        cmd_ships.name: cmd_ships,

        cmd_wslist.name: cmd_wslist,
        cmd_wsinit.name: cmd_wsinit,
        cmd_wsinfo.name: cmd_wsinfo,
        '__mandatory': True,
    },
    'management': {
        '__mandatory': False,
    },
    'moderation': {
        '__mandatory': False,
    }
}
