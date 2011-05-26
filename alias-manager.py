#!/usr/bin/python

import ConfigParser
import sys
import os
import optparse
import random

#import MySQLdb
import psycopg2

# list
# add
# remove
# disable
# enable

DEFAULT_CONFIG = {
    'database': {
        'host': None,
        'database': None,
        'table': None,
        'user': None,
        'password': None
        },
    }

def main(args):
    if len(args) < 2:
        usage(args)
        sys.exit(1)

    config = ConfigParser.SafeConfigParser(defaults=DEFAULT_CONFIG)
    add_defaults(config)
    config.read(os.path.expanduser('~/.alias-manager.conf'))
    # db = MySQLdb.connect(host = config.get('database', 'host'),
    #                      user = config.get('database', 'user'),
    #                      passwd = config.get('database', 'password'),
    #                      db = config.get('database', 'database'))
    db = psycopg2.connect('dbname=mail_aliases')
    
    op = args[1]
    if op == 'list':
        list_aliases(db, config, args[2:])
    elif op == 'add':
        add_alias(db, config, args[2:])
    elif op == 'remove':
        remove_alias(db, config, args[2:])
    elif op == 'disable':
        disable_alias(db, config, args[2:])
    elif op == 'enable':
        enable_alias(db, config, args[2:])
    else:
        usage()
        
def usage():
    pass
    
def list_aliases(db, config, args):
    if len(args) > 0:
        substr = '%' + args[0] + '%'
    else:
        substr = '%'
    sql = "SELECT alias, destination, enabled FROM aliases WHERE alias LIKE %s ORDER BY alias"
    cursor = db.cursor()
    cursor.execute(sql, (substr,))
    result = cursor.fetchall()
    max_alias_len = 0
    max_dest_len = 0
    for row in result:
        max_alias_len = max(max_alias_len, len(row[0]))
        max_dest_len = max(max_dest_len, len(row[1]))
    for row in result:
        if row[2] == 1:
            disabled = ''
        else:
            disabled = ' (disabled)'
        print(('{alias:'+str(max_alias_len)+'} -> {dest}{disabled}').format(alias = row[0], dest = row[1], disabled = disabled))
    
def add_alias(db, config, args):
    if len(args) == 0:
        return
    if config.getboolean('add', 'add-number'):
        digits = config.getint('add', 'num-digits')
        name = ("{base}-{number:0" + str(digits) + "}").format(base = args[0], number = gen_random(digits))
    else:
        name = args[0]
    dest = config.get('add', 'destination')
    sql = 'INSERT INTO aliases (alias, destination, enabled) VALUES (%s, %s, %s)'
    cursor = db.cursor()
    cursor.execute(sql, (name, dest, True))
    db.commit()
    print('Added alias ' + name)

def remove_alias(db, config, args):
    sql = 'DELETE FROM aliases WHERE alias = %s'
    cursor = db.cursor()
    cursor.execute(sql, (args[0],))
    db.commit()
    print('Deleted alias ' + args[0])

def disable_alias(db, config, args):
    sql = 'UPDATE aliases SET enabled = 0 WHERE alias = %s'
    cursor = db.cursor()
    cursor.execute(sql, (args[0],))
    db.commit()
    print('Disabled alias ' + args[0])

def enable_alias(db, config, args):
    sql = 'UPDATE aliases SET enabled = 1 WHERE alias = %s'
    cursor = db.cursor()
    cursor.execute(sql, (args[0],))
    db.commit()
    print('Enabled alias ' + args[0])

def add_defaults(config):
    if not config.has_section('add'):
        config.add_section('add')
    config.set('add', 'add-number', 'no')

def gen_random(digits):
    return random.randrange(10 ** digits)

if __name__ == "__main__":
    main(sys.argv)
