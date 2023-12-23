TODO: update instructions to talk about using Journal, rather than find report.

This is a set of simple scripts for getting data exported from QuickBooks into a free accounting system, started by Jonathan Corbet (corbet@lwn.net). They only support GnuCash for now; that is likely to change in the future.  For details on how they work and how to get your data out of QuickBooks, have a look at this article:

    https://lwn.net/Articles/729087/

Like so much of my code, these scripts have been developed to the point where they do what I needed, and not much further. Enhancements are gladly accepted, of course.

Please understand that neither I nor LWN can be responsible if these scripts mangle your accounting data in some way.  Ensuring the integrity of your data is your responsibility alone - look closely before you trust what these scripts produce!

# Usage Instructions

This is a rather careful process, and depending on your records you may still need to hand-edit a CSV file. So please pay close attention to the instructions and feel free to contribute to this documentation.

# Exporting data from Quickbooks

(NOTE: this may vary depending on your version of quickbooks, instructions are based on Jason.S's comment https://lwn.net/Articles/833616/ ).

## Part 1: Exporting Accounts (Customers, Vendors, etc.) from Quickbooks

1. Open QuickBooks and go to the Chart of Accounts

2. In the Chart of Accounts window:
Quickbooks 2022-2023: In the top of the window, make the 'View' set to 'All Accounts'.
Quickbooks 2017: Check "Include inactive" at the bottom to show all inactive/hidden accounts.

3. These scripts require that the accounts all have different names. Edit all accounts to be this way (double check subaccounts that may have the same name as other subaccounts). You can add numbers to the front of each to make them all uniquely named.

4. Remove forward slashes / from all account names (the scripts tripped up on this).

5. Export your Chart of Accounts and lists. 
Quickbooks 2022-2023: Go to File > Export > Lists to IIF Files... 
Quickbooks 2017: Go to File > Utilities > Export > Lists to IIF Files...

Select what is currently supported by the script: 
- Chart of Accounts (ACCNT)
- Customers (CUST)
- Vendors (VEND)
Click OK and save the IIF file somewhere, for this documentation we'll call this `quickbooks_exported_accounts-customers-vendors.iif`

6. You may want to do another separate IIF export file with everything selected, just in case you want to manually migrate things or improve the script later.

## Part 2: Exporting Journal from Quickbooks
  
1. Reconcile! Before doing anything, ensure all your transactions are reconciled/updated. The Journal export doesn't include reconciliation information, so we're assuming that your entries are already reconciled.

2. In QuickBooks, determine when the EARLIEST transaction entry that was ever made. If you don't know which account has the first transaction of all time, come up with a date that is definitely before when you started using QuickBooks. Some things that might help is browsing through various sections of 'Transaction Center' (but it may not show other earlier journal entries), or going through other records to see when the organization's books started.

2. Export your Journal transactions for all accounts of this company/book.
 
- Go to _Reports > Accountant & Taxes > Journal_ . 
- Select the Dates to be 'Custom Dates' going from the earliest date (determined in previous step) to today.
- In the top middle of the Journal window, there should be an 'Export to Excel' button. Click it, and it should open either Apple Numbers or Microsoft Excel.
- In your spreadsheet of the Journal, make the following changes 
  - remove the first empty column
  - the first three rows (report information)
  - remove the last row (total balance of debit & credit)
So you're left with just the header row (Trans #,	Type, Date, Num, ...) and the actual data. Export this as a CSV so it can be processed by the script. For this documentation we'll 

IMPORTANT: The values of dollar-value columns (Amount, Debit, Credit, Balance) in the CSV export needs to:
  - Have both the integer (dollar) and decimal (cents) value (e.g. `3.00`, not `3` ).
  - Not have quotes around the numbers (e.g. `3.00`, not `"3.00"`), 
  - Doesn't have double dashes for negative numbers (e.g. `-3.00`, not `--3.00`).
  - Doesn't have currency signs.
Generally you can fix this by formatting the columns as numbers with two decimal points. For this documentation we'll call this `quickbooks_exported_journal.csv`
 
- (NOTE: I recommend double-checking how many transaction entries are there too and encompass all dates. Have observed issue where opening a Numbers file in Libreoffice only shows 256 rows).

- (NOTE: the earlier version of these instructions & script made use of a 'Find Report' for transactions. This revised script instead uses the 'Journal' after noticing too many issues with the Find Report data)

# Importing data into GnuCash

## Environment setup

### Install GnuCash (with python bindings)

The scripts depend on a GnuCash installation that include an optional python bindings package. There's different approaches to set this up depending on your operating system:

- Make sure you've uninstalled any other binary distribution of GnuCash (e.g. executable downloaded from gnucash.org, flatpak, app store, etc.)

- Install GnuCash with python bindings.

**MacOS**: Install Python via MacPorts and the GnuCash Python bindings. Go to https://wiki.gnucash.org/wiki/Python_Bindings and follow the installation steps. /
NOTE: This path of installing MacPorts depends on also installing developer tools like XCode, which can take up several several gigs of storage.

**Debian-based Linux (e.g. Ubuntu)**: The apt package for GnuCash should include the python bindings, so run `sudo apt install gnucash`

**Redhat/Fedora-based Linux**: The rpm package for GnuCash should include python bindings, so run `sudo dnf install gnucash` 

(NOTE: You might need to modify a line in the scripts to point to the appropriate gnucash bindings package. For example, in a fedora installation I needed to 

### Downloading the scripts
On the computer with GnuCash, we need to download the scripts offered on this webpage you're reading this on. Assuming it's github, there should be a green 'Code' button with options to either clone this repository (using GIT) or 'download ZIP'.

- Go to the folder where you downloaded/clones the scripts, i.e. `cd /my/path/to/qb-escape`

- You may need to give the computer permission to run the scripts. On a unix machine (linux / macos), do this by `chmod 755 qb_iif_to_gc` and `chmod 755 qb_trans_to_gc` .

## Running script to import IIF file and create new GNUCash file

In a terminal window, let's import the iif file and create a new GNUCash file (which for example we'll call `gnucash_accountbook.gcf`:

- Run `qb_iif_to_gc /my/path/to/quickbooks_exported_accounts-customers-vendors.iif /my/path/to/gnucash_accountbook.gcf`

Did it run OK? Feel free to file an issue, or discuss on https://lists.gnucash.org/ . You can also try running it with a [sample IIF file](https://gist.github.com/seltzered/b124ba5c4f118d46dec4cc3da1febe06). 

Assuming it ran without errors, you should have an initial working `gnucash_accountbook.gcf` file. Try opening it, and going see the accounts imported so far (e.g. in GnuCash try going to 'Business > Customer > Customer Overview')

# Running script to import Journal CSV file into GNUCash file.

- Close GnuCash if you opened it in the previous step. We need to make sure there isn't a 'lock' on the file.

- In terminal window again, run `qb_trans_to_gc /my/path/to quickbooks_exported_journal.csv /my/path/to/gnucash_accountbook.gcf`

Did it run OK? Feel free to file an issue, or discuss on https://lists.gnucash.org/

Assuming it ran without errors,  you can see all transactions across accounts by going to Tools > General Journal, and going to View > Filter By... and select All Dates. 
