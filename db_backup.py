# Author: Michael Borden
# Date: Sun Dec 16, 2018
# 
# Purpose: Backup database with encryption and decription
#
# Example:
#   -- Backup (Encript)
#   : python3 db_backup.py -db databasename -u username@gmail.com -f/-d dumpname [-p num]
#   -- Restore
#   : python3 db_backup.py -r -db databasename -u username@gmail.com -f/-d dumpname [-p num]
#
# Note:
#   --Must first create a private key with GnuGP
#   : gpg[2] --gen-key
#   -- Then follow instructions and remember what you put in as you will need it


import os
import sys
import getopt
import time

# Default
restore = False
database = False
username = False
filename = False
directory = False
parallel = 1

# Get the user input
try:
    opts, _ = getopt.getopt(sys.argv[1:], 'r:u:b:f:d:p:', 
                            ['restore=', 'database=', 'username=', 'filename=', 
                             'directory=', 'parallel='])
except getopt.GetoptError:
    sys.exit()

# Parse the input
print('Reading ops...')
for opt, arg in opts:
    if (opt in ('-r', '--restore')):
        restore = True
    elif (opt in ('-b', '--database')):
        database = arg
    elif(opt in ('-u', '--username')):
        username = arg
    elif (opt in ('-f', '--filename')):
        filename = arg
    elif (opt in ('-d', '--directory')):
        directory = arg
    elif (opt in ('-p', '--parallel')):
        parallel = arg
    else:
        print('ERROR: Wrong input')
        sys.exit()

# Make sure you don't override anything. SAVE EVERYTHING!!!
if ((directory and os.path.isdir(directory)) or (filename and os.path.exists(filename))):
    print('ERROR: ALREADY EXISTS! Let\'s not override it.')
    sys.exit()
# Assure all the paramaters are given, and then either DCE or DUL
# Dump, Compress, Encrypt (DCE)
# Decrypt, Uncompress, Load (DUL)
else:
    if (not database):
        print('ERROR: Missing database name.')
    elif (filename and username):
        if (restore): # DUL
            print('Restoring...')
            os.system('gpg -d -o {}.decrypted {}'.format(filename, filename))
            os.system('tar xzf {}.tar.gz'.format(filename))
            os.system('pg_restore -j {} -d {} {}.tar.gz.gpg'.format(parallel, database, filename))
        else: # DCE
            print('Backing Up...')
            os.system('pg_dump -j {} -F d -f {} {}'.format(parallel, filename, database))
            os.system('tar czf {}.tar.gz {}'.format(filename, filename))
            os.system('gpg2 -e -r {} {}.tar.gz'.format(username, filename))
            #os.system('rm -rf {} && {}.tar.gz'.format(directory, directory)) ## iffy <security>
    elif (directory and username):
        if (restore): # DUL
            print('Restoring...')
            os.system('gpg -d -o {}.decrypted {}'.format(directory, directory))
            os.system('tar xzf {}.tar.gz'.format(directory))
            os.system('pg_restore -j {} -d {} {}.tar.gz.gpg'.format(parallel, database, directory))
        else: # DCE
            print('Backing Up...')
            os.system('pg_dump -j {} -F d -f {} {}'.format(parallel, directory, database))
            os.system('tar czf {}.tar.gz {}'.format(directory, directory))
            os.system('gpg2 -e -r {} {}.tar.gz'.format(username, directory))
            #os.system('rm {} && {}.tar.gz'.format(directory, directory)) ## iffy <security>
    else:
        print('ERROR: Missing filename (-f), directory (-d), or username (-u)')
        sys.exit()

