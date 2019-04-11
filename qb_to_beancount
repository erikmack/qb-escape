#!/usr/bin/python3
#
# Import quickbooks data to beancount
#
# See https://lwn.net/Articles/785553/ for the article that describes
# this program.  Note that I got it far enough to demonstrate the concept,
# but have certainly not turned it into anything generally useful.
#
# Copyright 2017 Jonathan Corbet.
# This program may be distributed under the terms of the GNU General
# Public License, version 2 or later.
#
# This program is provided with no warranty of any kind.  You, and only
# you, are responsible for the integrity of your accounting data.
#
import sys, re, argparse, os, csv
import iif
import remap

#
# Start with IIF importing stuff for the chart of accounts.
#
AccountTypeMap = {
    'BANK':	'Assets',
    'CCARD':	'Liabilities',
    'OCASSET':	'Assets',
    'OASSET':	'Assets',
    'FIXASSET':	'Assets',
    'AP':	'Liabilities',
    'AR':	'Assets',
    'OCLIAB':	'Liabilities',
    'LTLIAB':	'Liabilities',
    'EQUITY':	'Equity',
    'INC':	'Income',
    'EXP':	'Expenses',
    'EXINC':	'Income',
    'EXEXP':	'Expenses',
    }

def lookup_acct_type(type):
    try:
        return AccountTypeMap[type]
    except KeyError:
        return 'Unknown'
#
# Transform account names.  For now, just remove slashes, since they
# make GnuCash confused and unhappy.
#
def fixup_acct_name(name):
    return name.replace('/', '').replace(' ', '').replace('&','')

#
# Import a list of accounts.
#
AccountMap = { }
def import_accounts(list):
    for entry in list.entries:
        #
        # Figure out the type and do remapping/reparenting.
        #
        type = lookup_acct_type(entry['ACCNTTYPE'])
        name = '%s:%s' % (type, fixup_acct_name(remap.remap(entry['NAME'])))
        basename = entry['NAME'].split(':')[-1]
        AccountMap[basename] = name
        emit('2000-01-01 open %s USD' % (name))

#
# OK, move on to CSV transaction import.
#
def FixDate(date):
    month, day, year = map(int, date.split('/'))
    # Handle old, two digit dates with an arbitrary 1980 pivot
    if year < 100:
        if year < 80:
            year = year + 2000;
        else:
            year = year + 1900
    return '%d-%02d-%02d' % (year, month, day)

def ReadTransaction(reader):
    entry = next(reader)
    #
    # QB helpfully puts in a couple of crap lines with an empty
    # name.  Drop them.
    #
    if entry['']:
        return
    #
    # Set up the overall transaction.
    #
    name = entry['Name']
    desc = entry['Memo']
    date = FixDate(entry['Date'])
    emit('%s txn "%s" "%s"' % (date, name, desc))
    if entry['Num']:
        emit('  number: "%s"' % (entry['Num']))
    if entry['Clr'] != 'X':
        emit('  rec: "n"')
    else:
        emit('  rec: "y"')
    #
    # Basic theory here: QB dumps a pile of splits into the file
    # without grouping them into transactions.  The signal that we've
    # found the last split is that the balance goes to zero.  This
    # *could* screw us, since that is possible in a legitimate transaction.
    # But with luck it won't actually happen.
    #
    # Note the the overall entry is also the first split.
    #
    while True:
        #
        # Occasionally the amount is an empty string.  That seems to come
        # from a zeroed-out split that wasn't removed from the transaction;
        # simply ignore it.
        #
        if not entry['Amount']:
            entry = next(reader)
            continue
        #
        # Put together the split info.
        #
        amount = entry['Amount']
        account = AccountMap[entry['Account']]
        if not account:
            print('Unknown account', entry['Account'])
            account = 'Expenses:Miscellaneous'
        emit('  %-24s %s USD ; %s' % (account, amount, entry['Memo']))
        #
        # Are we done?
        # The last entry will be '0.00' as a string. If we do a numeric
        # conversion to test against zero, we'd have to worry about commas
        # and other issues, so opt for similicity.
        #
        if entry['Balance'] == '0.00':
            break
        entry = next(reader)
    emit('')


#
# Here we do the argparsery
#
def setupargs():
    p = argparse.ArgumentParser()
    p.add_argument('-m', '--mapfile', required = False, default = None,
                   help = 'Name of account-name remapping file')
    p.add_argument('-o', '--output', required = False, default = None,
                   help = 'Name of the output file')
    p.add_argument('iif', help = 'The IIF names file to process')
    p.add_argument('csvfile', help = 'The CSV transaction file')
    return p

def croak(message):
    sys.stderr.write(message)
    sys.stderr.flush()
    sys.exit(1)

def emit(s):
    output.write(s)
    output.write('\n')
#
# Main program time.
#

#
# Check args and open files
#
args = setupargs().parse_args()

try:
    lists = iif.read_IIF(open(args.iif, 'r', encoding='latin1'))
except IOError as e:
    croak('Unable to open %s, %s' % (args.iif, e))
try:
    tfile = open(args.csvfile, 'r', encoding='latin1')
except IOError as e:
    croak('Unable to open %s, %s' % (args.csvfile, e))

if args.output:
    output = open(args.output, 'w', encoding = 'utf8')
else:
    output = sys.stdout
#
# Load the mapfile if there is one.
#
if args.mapfile:
    remap.load_mapfile(args.mapfile)

#
# Import the lists we understand.
#
Ilist = [ ('ACCNT', import_accounts) ]

for name, importer in Ilist:
    try:
        importer(lists[name])
    except KeyError:
        pass

#
# Import the transaction data.
#
reader = csv.DictReader(tfile)
while True:
    try:
        ReadTransaction(reader)
    except StopIteration:
        break

sys.exit(0)
