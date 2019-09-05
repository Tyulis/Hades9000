# -*- coding:utf-8 -*-

import pprint

gameids = {
    'TransportCapacity': 'module.trade.extension',
    'ShipmentComputer': 'module.trade.computer',
    'Trader': 'module.trade.boost',
    'Rush': 'module.trade.rush',
    'TradeBurst': 'module.trade.burst',
    'ShipmentBeam': 'module.trade.beam',
    'ShipmentDrone': 'module.trade.drone',
    'Offload': 'module.trade.offload',
    'Entrust': 'module.trade.entrust',
    'Dispatch': 'module.trade.dispatch',
    'Recall': 'module.trade.recall',

    'MiningBoost': 'module.mining.boost',
    'MineralStorageCapacity': 'module.mining.extension',
    'Enrich': 'module.mining.enrich',
    'MassMining': 'module.mining.remote',
    'HydrogenUpload': 'module.mining.upload',
    'MiningUnity': 'module.mining.unity',
    'Crunch': 'module.mining.crunch',
    'Genesis': 'module.mining.genesis',
    'HydroRocket': 'module.mining.rocket',
    'MiningDrone': 'module.mining.drone',

    'WeakShield': 'module.shield.alpha',
    'StandardShield': 'module.shield.delta',
    'StrongShield': 'module.shield.omega',
    'PassiveShield': 'module.shield.passive',
    'MirrorShield': 'module.shield.mirror',
    'BlastShield': 'module.shield.blast',
    'AreaShield': 'module.shield.area',

    'WeakBattery': 'module.weapon.none',
    'Battery': 'module.weapon.battery',
    'Laser': 'module.weapon.laser',
    'MassBattery': 'module.weapon.mass-battery',
    'DualLaser': 'module.weapon.dual-laser',
    'Barrage': 'module.weapon.barrage',
    'DartLauncher': 'module.weapon.dart',

    'EMP': 'module.support.emp',
    'Repair': 'module.support.repair',
    'Teleport': 'module.support.teleport',
    'TimeWarp': 'module.support.warp',
    'RedStarExtender': 'module.support.rse',
    'Stealth': 'module.support.stealth',
    'Unity': 'module.support.unity',
    'Fortify': 'module.support.fortify',
    'Sanctuary': 'module.support.sanctuary',
    'AlphaRocket': 'module.support.alpha-rocket',
    'Salvage': 'module.support.salvage',
    'Supress': 'module.support.suppress',
    'Destiny': 'module.support.destiny',
    'Barrier': 'module.support.barrier',
    'Impulse': 'module.support.impulse',
    'Vengeance': 'module.support.vengeance',
    'DeltaRocket': 'module.support.delta-rocket',
    'Leap': 'module.support.leap',
    'Bond': 'module.support.bond',
    'AlphaDrone': 'module.support.drone',
    'OmegaRocket': 'module.support.omega-rocket',

    'GuardianBattery': 'module.cerberus.guardian-battery',
    'PhoenixShield': 'module.cerberus.phoenix-shield',
    'DestroyerVengeance': 'module.cerberus.destroyer-vengeance',
    'BomberLauncher': 'module.cerberus.bomber-rocket',
    'ColossusLaser': 'module.cerberus.colossus-laser',
    'DartBarrage': 'module.cerberus.dart-barrage',
    'InterceptorMBattery': 'module.cerberus.interceptor-mass-battery',
}

USELESS_COLUMNS = ('Name', 'Icon', 'TID', 'TID_Description', 'WeaponFx', 'ClientActivationFx', 'ActivateFX', 'ActivateFXStaysInPlace', 'SustainedFX', 'ScaleEffectsWithZoom', 'WeaponEffectType')

def data_convert(colname, value):
    if value is None:
        return (colname, value)
    if colname == 'APTPIOTTP':
        converted = value / 5
    elif colname == 'FuelUseIncrease':
        converted = value / 5
    elif colname == 'AllowedStarTypes':
        converted = 'YS' if value == 0 else 'RS'
    elif colname == 'AwardLevel':
        converted = value + 1
    elif 'EffectDurationx10' in colname:
        converted = value / 10
    elif 'EffectRadius' in colname:
        converted = round(value / 10, 1)
    elif colname == 'MiningSpeedModifierPct':
        converted = value / 100
    elif colname in ('TimeWarpFactor', 'TradeStationDeliverReward'):
        converted = value / 100
    elif colname == 'ActivationPrepWS':
        converted = value * 600
    else:
        converted = value
    return colname, converted

def generate(infile, outfile):
    with open(infile, 'r') as f:
        csvdata = f.read()
    lines = csvdata.splitlines()
    lcolnames, lmodules = lines[0], lines[1:]
    colnames = lcolnames.split(',')
    codecol = colnames.index('Name')
    modules = {}
    for line in lmodules:
        linedata = line.split(',')
        linedata = [(None if item == '' else (int(item) if item.isdigit() else item)) for item in linedata]
        code = linedata[codecol]
        if code is not None:
            lastcode = gameids[code]
            modules[gameids[code]] = []
            level = 1
        data = dict([data_convert(colnames[i], linedata[i]) for i in range(len(colnames)) if colnames[i] not in USELESS_COLUMNS])
        if data['SalvageHullPercent'] is not None:
            data['SalvageHullPercentWS'] = int(data['SalvageHullPercent'].split('!')[1])
            data['SalvageHullPercentBS'] = int(data['SalvageHullPercent'].split('!')[2])
            data['SalvageHullPercent'] = int(data['SalvageHullPercent'].split('!')[0])
        else:
            data['SalvageHullPercentWS'] = data['SalvageHullPercentBS'] = data['SalvageHullPercent'] = None
        data['Level'] = level
        level += 1
        modules[lastcode].append(data)
    for module in modules:
        if modules[module][0]['SlotType'] == 'Support':
            modules[module][0]['AwardLevel'] += 1
    with open(outfile, 'w') as f:
        f.write('_MODULE_DATA = ')
        f.write(pprint.pformat(modules))


if __name__ == '__main__':
    generate('modules.csv', 'moduledata.py')
