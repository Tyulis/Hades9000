import math
from .moduledata import _MODULE_DATA
from .modulestats import *
from .shipdata import _SHIP_DATA

modules = {'trade': [], 'mining': [], 'weapon': [], 'shield': [], 'support': []}

"""modules['trade'] = (
	'module.trade.extension',
	'module.trade.computer',
	'module.trade.boost',
	'module.trade.rush',
	'module.trade.burst',
	'module.trade.drone',
	'module.trade.offload',
	'module.trade.beam',
	'module.trade.entrust',
	'module.trade.dispatch',
	'module.trade.recall',
	'module.trade.none',
)

modules['mining'] = (
	'module.mining.boost',
	'module.mining.extension',
	'module.mining.enrich',
	'module.mining.remote',
	'module.mining.upload',
	'module.mining.unity',
	'module.mining.crunch',
	'module.mining.genesis',
	'module.mining.rocket',
	'module.mining.drone',
	'module.mining.none',
)

modules['weapon'] = (
	'module.weapon.none',
	'module.weapon.battery',
	'module.weapon.laser',
	'module.weapon.mass-battery',
	'module.weapon.dual-laser',
	'module.weapon.barrage',
	'module.weapon.dart',
)

modules['shield'] = (
	'module.shield.alpha',
	'module.shield.delta',
	'module.shield.passive',
	'module.shield.omega',
	'module.shield.mirror',
	'module.shield.blast',
	'module.shield.area',
	'module.shield.none',
)

modules['support'] = (
	'module.support.emp',
	'module.support.teleport',
	'module.support.rse',
	'module.support.repair',
	'module.support.warp',
	'module.support.unity',
	'module.support.sanctuary',
	'module.support.stealth',
	'module.support.fortify',
	'module.support.impulse',
	'module.support.alpha-rocket',
	'module.support.salvage',
	'module.support.suppress',
	'module.support.destiny',
	'module.support.barrier',
	'module.support.vengeance',
	'module.support.delta-rocket',
	'module.support.leap',
	'module.support.bond',
	'module.support.drone',
	'module.support.omega-rocket',
	'module.support.none',
)"""

for modname in _MODULE_DATA.keys():
	if 'cerberus' not in modname:
		modules[_MODULE_DATA[modname][0]['SlotType'].lower()].append(modname)
modules['trade'].sort(key=lambda name: _MODULE_DATA[name][0]['AwardLevel'])
modules['mining'].sort(key=lambda name: _MODULE_DATA[name][0]['AwardLevel'])
modules['weapon'].sort(key=lambda name: _MODULE_DATA[name][0]['AwardLevel'])
modules['shield'].sort(key=lambda name: _MODULE_DATA[name][0]['AwardLevel'])
modules['support'].sort(key=lambda name: _MODULE_DATA[name][0]['AwardLevel'])
modules['trade'].append('module.trade.none')
modules['mining'].append('module.mining.none')
modules['shield'].append('module.shield.none')
modules['support'].append('module.support.none')

module_names = {
	'FR': {
		'module.trade.extension': 'Extension de l\'aire de chargement',
		'module.trade.computer': 'IA de cargaisons',
		'module.trade.boost': 'Bonus d\'échange',
		'module.trade.rush': 'Ruée',
		'module.trade.burst': 'Poussée d\'échange',
		'module.trade.drone': 'Drone de cargaisons',
		'module.trade.offload': 'Déchargement',
		'module.trade.beam': 'Rayon de cargaisons',
		'module.trade.entrust': 'Confiance',
		'module.trade.dispatch': 'Expédition',
		'module.trade.recall': 'Rappel',
		'module.trade.none': 'Vide',

		'module.mining.boost': 'Bonus de forage',
		'module.mining.extension': 'Extension de stockage d\'hydrogène',
		'module.mining.enrich': 'Enrichissement',
		'module.mining.remote': 'Forage à distance',
		'module.mining.upload': 'Transfert d\'hydrogène',
		'module.mining.unity': 'Unité de forage',
		'module.mining.crunch': 'Pénurie',
		'module.mining.genesis': 'Génèse',
		'module.mining.rocket': 'Roquette à hydrogène',
		'module.mining.drone': 'Drone de forage',
		'module.mining.none': 'Vide',

		'module.weapon.none': 'Canon faible',
		'module.weapon.battery': 'Canon',
		'module.weapon.laser': 'Laser',
		'module.weapon.mass-battery': 'Batterie multiple',
		'module.weapon.dual-laser': 'Double laser',
		'module.weapon.barrage': 'Barrage',
		'module.weapon.dart': 'Dart',

		'module.shield.alpha': 'Bouclier alpha',
		'module.shield.delta': 'Bouclier delta',
		'module.shield.passive': 'Bouclier passif',
		'module.shield.omega': 'Bouclier oméga',
		'module.shield.mirror': 'Bouclier miroir',
		'module.shield.blast': 'Bouclier balistique',
		'module.shield.area': 'Bouclier de zone',
		'module.shield.none': 'Vide',

		'module.support.emp': 'IEM',
		'module.support.teleport': 'Téléport',
		'module.support.rse': 'Extension de vie d\'étoile rouge',
		'module.support.repair': 'Réparation à distance',
		'module.support.warp': 'Distortion temporelle',
		'module.support.unity': 'Unité',
		'module.support.sanctuary': 'Sanctuaire',
		'module.support.stealth': 'Discrétion',
		'module.support.fortify': 'Fortification',
		'module.support.impulse': 'Impulsion',
		'module.support.alpha-rocket': 'Roquette alpha',
		'module.support.salvage': 'Sauvetage',
		'module.support.suppress': 'Suppression',
		'module.support.destiny': 'Destinée',
		'module.support.barrier': 'Barrière',
		'module.support.vengeance': 'Vengeance',
		'module.support.delta-rocket': 'Roquette delta',
		'module.support.leap': 'Bond',
		'module.support.bond': 'Lien',
		'module.support.drone': 'Drone alpha',
		'module.support.omega-rocket': 'Roquette oméga',
		'module.support.none': 'Vide',

		'module.cerberus.guardian-battery': 'Canon (gardien)',
		'module.cerberus.interceptor-mass-battery': 'Batterie multiple (intercepteur)',
		'module.cerberus.colossus-laser': 'Laser (colosse)',
		'module.cerberus.destroyer-vengeance': 'Vengeance (destroyer)',
		'module.cerberus.phoenix-shield': 'Bouclier de zone (phoenix)',
		'module.cerberus.bomber-rocket': 'Roquette (bombardier)',
		'module.cerberus.dart-barrage': 'Barrage Dart (tempête)',

		'module.none.none': 'Vide',
	}
}

all_modules = modules['trade'] + modules['mining'] + modules['weapon'] + modules['shield'] + modules['support']

ship_modules = {
	'ship.player.battleship': {
		'trade': [0],
		'mining': [0],
		'weapon': [0],
		'shield': [0],
		'support': [0],
	},
	'ship.player.miner': {
		'trade': [0],
		'mining': [0],
		'weapon': [0],
		'shield': [0],
		'support': [0],
	},
	'ship.player.transport':{
		'trade': [0],
		'mining': [0],
		'weapon': [0],
		'shield': [0],
		'support': [0],
	},
}

for shiptype in ship_modules:
	shipdata = _SHIP_DATA[shiptype]
	for level in shipdata:
		for moduletype in ship_modules[shiptype]:
			ship_modules[shiptype][moduletype].append(ship_modules[shiptype][moduletype][-1])
		for moduletype in level['NewModuleSlots'].split('!'):
			ship_modules[shiptype][moduletype.lower()][-1] += 1


ship_types = ('ship.player.battleship', 'ship.player.miner', 'ship.player.transport')

ship_names = {
	'FR': {
		'ship.player.battleship': 'Cuirassé',
		'ship.player.miner': 'Foreur',
		'ship.player.transport': 'Transport'
	},
}

corp_levels = (0, 1, 30, 100, 250, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000)
corp_passivebonus = (1, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18, 1.2, 1.22, 1.24, 1.26, 1.28, 1.3)
corp_rsbonus = (1, 1.01, 1.02, 1.03, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18, 1.2, 1.2, 1.2, 1.2)

ws_states = {
	'ws.state.future': 'Prévision',
	'ws.state.inscriptions': 'Inscriptions ouvertes',
	'ws.state.idle': 'En attente',
	'ws.state.running': 'En cours',
	'ws.state.ended': 'Terminée',
}

max_rslevel = 10

def module_data(module, level, info):
	return _MODULE_DATA[module][level - 1][info]

def ship_data(ship, level, info):
	return _SHIP_DATA[ship][level - 1][info]

def credits_score(price):
	return 5 * math.sqrt(price)

def blueprints_score(blueprints):
	return 10 * math.sqrt(blueprints)

def ship_score(type, level):
	return int(credits_score(sum([ship_data(type, tlevel, 'DesignUpgradeCost') for tlevel in range(1, level + 1)]) * 1.7))

def module_score(code, level):
	if level <= 0:
		return 0
	blueprints = module_data(code, level, 'UnlockBlueprints')
	credits = sum([module_data(code, tlevel, 'UnlockPrice') for tlevel in range(1, level + 1)])
	rslevel = module_data(code, 1, 'AwardLevel')
	#print("%s : %.3f, %.3f, %.1f" % (code, credits_score(credits), blueprints_score(blueprints), (1 + rslevel / 5)))
	return int(((credits_score(credits) + blueprints_score(blueprints)) / 2) * (1 + rslevel / 5))

def transport_capacity(tslevel, cbelevel):
	return ship_data('ship.player.transport', tslevel, 'JobCapacity') + module_data('module.trade.extension', cbelevel, 'ExtraTradeSlots')
