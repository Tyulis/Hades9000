# -*- coding:utf-8 -*-

import pprint

def generate(infile, outfile):
    with open(infile, 'r') as f:
        csvdata = f.read()
    lines = csvdata.splitlines()
    lcolnames, lmodules = lines[0], lines[1:]
    colnames = lcolnames.split(',')
    codecol = colnames.index('Code')
    modules = {}
    for line in lmodules:
        linedata = line.split(',')
        linedata = [(None if item == '' else (int(item) if item.isdigit() else item)) for item in linedata]
        code = linedata[codecol]
        if code is not None:
            lastcode = code
            modules[code] = []
        data = {colnames[i]: linedata[i] for i in range(len(colnames)) if colnames[i] not in ('Name', 'Code')}
        modules[lastcode].append(data)
    with open(outfile, 'w') as f:
        f.write('moduledata = ')
        f.write(pprint.pformat(modules))


if __name__ == '__main__':
    generate('modules.csv', 'moduledata.py')
