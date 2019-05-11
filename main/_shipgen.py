# -*- coding:utf-8 -*-

import pprint

gameids = {
    'Transport': 'ship.player.transport',
    'Miner': 'ship.player.miner',
    'Battleship': 'ship.player.battleship',

    'CerberusSentinel': 'ship.cerberus.sentinel',
    'CerberusGuardian': 'ship.cerberus.guardian',
    'CerberusColossus': 'ship.cerberus.colossus',
    'CerberusInterceptor': 'ship.cerberus.interceptor',
    'CerberusDestroyer': 'ship.cerberus.destroyer',
    'CerberusPhoenix': 'ship.cerberus.phoenix',
    'CerberusBomber': 'ship.cerberus.bomber',
    'CerberusStorm': 'ship.cerberus.storm',

    'AlphaDrone': 'ship.drone.alpha',
    'ShipmentDrone': 'ship.drone.shipment',
    'MiningDrone': 'ship.drone.mining',

    'TutBattleship': 'ship.special.tutorial-battleship',
    'BlueStarBot': 'ship.special.blue-star-bot',
}

USELESS_COLUMNS = ('Name', 'ConceptImage', 'Model', 'ModelScale', 'TID', 'TID_Description', 'TID_INFO_SCREEN', 'TID_UPGRADE')

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
        data = {colnames[i]: linedata[i] for i in range(len(colnames)) if colnames[i] not in USELESS_COLUMNS}
        modules[lastcode].append(data)
    with open(outfile, 'w') as f:
        f.write('_SHIP_DATA = ')
        f.write(pprint.pformat(modules))


if __name__ == '__main__':
    generate('capital_ships.csv', 'shipdata.py')
