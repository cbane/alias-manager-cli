#!/usr/bin/env python

from __future__ import print_function

from ConfigParser import SafeConfigParser
from configobj import ConfigObj
from validate import Validator
from argparse import ArgumentParser
import random
import os.path

from pprint import pprint

from aliasmanager import *

CONFIGSPEC = {
    'database': {
        'driver': 'string',
        'host': 'string(default=None)',
        'port': 'integer(default=None)',
        'dbname': 'string',
        'table': 'string(default=None)',
        'user': 'string(default=None)',
        'password': 'string(default=None)',
        },
    'add': {
        'digits': 'integer(min=0, default=0)',
        'target': 'string(default=None)',
        }
    }

def main():
    config = ConfigObj('alias-manager.conf', configspec=CONFIGSPEC)
    val = Validator()
    result = config.validate(val)
    if result != True:
        raise SystemExit('Error loading config file')
    
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='command')

    parser_list = subparsers.add_parser('list', help='list aliases')
    parser_list.add_argument('alias', metavar='ALIAS', nargs='?',
                             help='Alias (or substring) to search for')
    parser_list.set_defaults(func=list_cmd)
    
    parser_add = subparsers.add_parser('add', help='add an alias')
    parser_add.add_argument('-d', '--digits', metavar='DIGITS', type=int,
                            default=config['add']['digits'],
                            help='number of digits to add')
    parser_add.add_argument('alias', metavar='ALIAS', help='alias to add')
    parser_add.add_argument('target', metavar='TARGET', nargs='?',
                            default=config['add']['target'],
                            help='target of alias')
    parser_add.set_defaults(func=add_cmd)
    
    parser_remove = subparsers.add_parser('remove', help='remove an alias')
    parser_remove.add_argument('alias', metavar='ALIAS', help='alias to remove')
    parser_remove.set_defaults(func=remove_cmd)
    
    parser_enable = subparsers.add_parser('enable', help='enable an alias')
    parser_enable.add_argument('alias', metavar='ALIAS', help='alias to enable')
    parser_enable.set_defaults(func=enable_cmd, enabled=True)
    
    parser_disable = subparsers.add_parser('disable', help='disable an alias')
    parser_disable.add_argument('alias', metavar='ALIAS', help='alias to disable')
    parser_disable.set_defaults(func=enable_cmd, enabled=False)
    
    args = parser.parse_args()
    session = init_db(config=config['database'], echo=True)
    args.func(session, args)
        
def list_cmd(session, args):
    if args.alias:
        search = '%{0}%'.format(args.alias)
    else:
        search = '%'
    aliases = session.query(Alias).filter(Alias.alias.like(search)).order_by(Alias.alias).all()

    max_len = reduce(max, [len(alias.alias) for alias in aliases], 0)

    for alias in aliases:
        if alias.enabled:
            disabled = ''
        else:
            disabled = ' (disabled)'
        print('{0.alias:{1}} -> {0.destination}{2}'.format(alias, max_len, disabled))
    
def add_cmd(session, args):
    if args.digits > 0:
        alias_str = '{0}-{1:0{2}}'.format(args.alias, gen_random(args.digits),
                                          args.digits)
    else:
        alias_str = args.alias
    alias = Alias(alias_str, 'asdf')
    session.add(alias)
    session.commit()
    print('Added alias {}'.format(alias_str))

def remove_cmd(session, args):
    query = session.query(Alias).filter(Alias.alias==args.alias)

    if not query.first():
        raise NoSuchAlias(args.alias)
    
    query.delete()
    session.commit()
    print('Deleted alias {}'.format(args.alias))

def enable_cmd(session, args):
    if args.enabled:
        op = 'Enabled'
    else:
        op = 'Disabled'
    alias = session.query(Alias).filter(Alias.alias==args.alias).first()
    if not alias:
        raise NoSuchAlias(args.alias)
    alias.enabled = enabled
    session.commit()
    print('{} alias {}'.format(op, alias.alias))

def gen_random(digits):
    return random.randrange(10 ** digits)

class NoSuchAlias(SystemExit):
    def __init__(self, alias):
        super().__init__('No such alias: {}'.format(alias))

if __name__ == "__main__":
    main()
