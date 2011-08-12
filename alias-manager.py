#!/usr/bin/env python

from __future__ import print_function

from ConfigParser import SafeConfigParser
from argparse import ArgumentParser
import random
import os.path

from pprint import pprint

from aliasmanager import *

DEFAULT_CONFIG = {
    'database': {
        'host': None,
        'dbname': None,
        'table': None,
        'user': None,
        'password': None
        },
    'add': {
        'digits': 0,
        'target': None,
        },
    }

def config_dict(config):
    ret = {}
    for section in config.sections():
        print('Section: %s' % section)
        ret[section] = {}
        for option, value in config.items(section):
            print('  Option: %s' % option)
            ret[section][option] = value
    return ret

def init_config(config):
    for section in DEFAULT_CONFIG.keys():
        if not config.has_section(section):
            config.add_section(section)

def main():
    # #config = SafeConfigParser(defaults=DEFAULT_CONFIG)
    # config = SafeConfigParser()
    # config.read(['alias-manager.conf',
    #              os.path.expanduser('~/.alias-manager.conf')])
    # pprint(config.defaults())
    # pprint(config_dict(config))
    
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='command')

    parser_list = subparsers.add_parser('list', help='list aliases')
    parser_list.add_argument('alias', metavar='ALIAS', nargs='?',
                             help='Alias (or substring) to search for')
    
    parser_add = subparsers.add_parser('add', help='add an alias')
    parser_add.add_argument('-d', '--digits', metavar='DIGITS', type=int, default=0,
                            help='number of digits to add')
    parser_add.add_argument('alias', metavar='ALIAS', help='alias to add')
    parser_add.add_argument('target', metavar='TARGET', nargs='?',
                            help='target of alias')
    
    parser_remove = subparsers.add_parser('remove', help='remove an alias')
    parser_remove.add_argument('alias', metavar='ALIAS', help='alias to remove')
    
    parser_enable = subparsers.add_parser('enable', help='enable an alias')
    parser_enable.add_argument('alias', metavar='ALIAS', help='alias to enable')
    
    parser_disable = subparsers.add_parser('disable', help='disable an alias')
    parser_disable.add_argument('alias', metavar='ALIAS', help='alias to disable')
    
    args = parser.parse_args()

    session = init_db('sqlite:///aliases.sqlite')

    if args.command == 'list':
        list_aliases(session, args)
    elif args.command == 'add':
        add_alias(session, args)
    elif args.command in ('remove', 'rm', 'delete'):
        remove_alias(session, args)
    elif args.command == 'enable':
        enable_alias(session, args, True)
    elif args.command == 'disable':
        enable_alias(session, args, False)
    else:
        print('Unknown command: {}'.format(args.command))
        
def list_aliases(session, args):
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
    
def add_alias(session, args):
    if args.digits > 0:
        alias_str = '{0}-{1:0{2}}'.format(args.alias, gen_random(args.digits),
                                          args.digits)
    else:
        alias_str = args.alias
    alias = Alias(alias_str, 'asdf')
    session.add(alias)
    session.commit()
    print('Added alias {}'.format(alias_str))

def remove_alias(session, args):
    query = session.query(Alias).filter(Alias.alias==args.alias)

    if not query.first():
        raise NoSuchAlias(args.alias)
    
    query.delete()
    session.commit()
    print('Deleted alias {}'.format(args.alias))

def enable_alias(session, args, enabled):
    if enabled:
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
