#
# A crude IIF importer.  How can it be that nobody ever wrote one of these?
#
# Copyright 2017 Jonathan Corbet.
# This program may be distributed under the terms of the GNU General
# Public License, version 2 or later.
#
from __future__ import print_function

class IIF_list:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.entries = []

def HeaderLine(line):
    if line[0] != '!':
        print('Funky line "%s"' % (line))
        return None
    sline = line[1:].split('\t')
    return IIF_list(sline[0], sline[1:])

def strip_quotes(s):
    if s and (s[0] == s[-1] == '"'):
        return s[1:-1]
    return s

def IIF_Entry(list, line):
    sline = line.split('\t')
    if sline[0] != list.name:
        print('List %s, line starts with %s!' % (list.name, sline[0]))
    else:
        e = { }
        for i in range(0, len(list.fields)):
            e[list.fields[i]] = strip_quotes(sline[i + 1])
        list.entries.append(e)

def read_IIF(file):
    lists = { }
    current = None
    for line in file.readlines():
        while line[-1] in ['\r', '\n']:
            line = line[:-1] # can't use rstrip(), need the tabs
        #
        # Begin state (current is None): we should have a header line
        # here.
        #
        if not current:
            current = HeaderLine(line)
            if current:
                lists[current.name] = current
            continue
        #
        # Otherwise we have an open list.  There are a couple of funky
        # useless entries that QB tosses in, look for them now.
        #
        end = 'END' + current.name
        if line == end:
            current = None
            continue
        if line == '!' + end:
            continue
        #
        # If it starts with '!', we're starting a new list.
        #
        if line[0] == '!':
            current = HeaderLine(line)
            if current:
                lists[current.name] = current
            continue
        #
        # Otherwise it damn well better be a list entry.
        #
        IIF_Entry(current, line)
    return lists

