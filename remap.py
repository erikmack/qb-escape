#
# A really simple account-name remapping module.
#
# Copyright 2017 Jonathan Corbet.
# This program may be distributed under the terms of the GNU General
# Public License, version 2 or later.
#
from __future__ import print_function

Mappings = { }

def load_mapfile(file):
    try:
        mf = open(file, 'r')
    except IOError:
        print('Unable to open map file %s, doing without' % (file))
        return
    for line in mf.readlines():
        if not line or line[0] == '#':
            continue
        sline = line.split('|')
        if len(sline) != 2:
            print('Funky map line:', line)
            continue
        Mappings[sline[0].strip()] = sline[1].strip()
    mf.close()

def remap(acct):
    try:
        return Mappings[acct]
    except KeyError:
        smap = acct.split(':')
        try:
            return Mappings[smap[-1]]
        except KeyError:
            return acct
