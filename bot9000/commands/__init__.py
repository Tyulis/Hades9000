# -*- coding:utf-8 -*-

from .help import *
from .account import *
from .hadesstar import *
from .management import *
from .utilities import *
from .faq import *


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
        cmd_corpkick.name: cmd_corpkick,
        cmd_setchannel.name: cmd_setchannel,
        cmd_usedroles.name: cmd_usedroles,
        cmd_setrole.name: cmd_setrole,
        cmd_togglemodule.name: cmd_togglemodule,
        cmd_groupinfo.name: cmd_groupinfo,
        cmd_corpinfo.name: cmd_corpinfo,
        cmd_update.name: cmd_update,
        '__mandatory': True,
    },
    'hadesstar': {
        cmd_playerinfo.name: cmd_playerinfo,
        cmd_setinfo.name: cmd_setinfo,
        cmd_techs.name: cmd_techs,
        cmd_techids.name: cmd_techids,
        cmd_settech.name: cmd_settech,
        cmd_techlist.name : cmd_techlist,
        cmd_ships.name: cmd_ships,
        cmd_modinfo.name: cmd_modinfo,
        '__mandatory': True,
    },
    'whitestar': {
        cmd_wslist.name: cmd_wslist,
        cmd_wsinit.name: cmd_wsinit,
        cmd_wsinfo.name: cmd_wsinfo,
        cmd_wsregister.name: cmd_wsregister,
        cmd_wsstate.name: cmd_wsstate,
        cmd_wsrun.name: cmd_wsrun,
        cmd_wsend.name: cmd_wsend,
        '__mandatory': False,
    },
    'redstar': {
        cmd_rsin.name: cmd_rsin,
        cmd_rsout.name: cmd_rsout,
        cmd_rsshout.name: cmd_rsshout,
        cmd_rsping.name: cmd_rsping,
        cmd_rsqueue.name: cmd_rsqueue,
        cmd_rsready.name: cmd_rsready,
        cmd_rsunready.name: cmd_rsunready,
        '__mandatory': False,
    },
    'faq': {
        cmd_question.name: cmd_question,
        cmd_answer.name: cmd_answer,
        cmd_qsearch.name: cmd_qsearch,
        cmd_qlook.name: cmd_qlook,
        '__mandatory': False,
    },
    'management': {
        cmd_del.name: cmd_del,
        '__mandatory': False,
    },
    'utilities': {
        cmd_time.name : cmd_time,
        cmd_afk.name: cmd_afk,
        cmd_back.name: cmd_back,
        cmd_isafk.name: cmd_isafk,
        '__mandatory': False,
    }
}
