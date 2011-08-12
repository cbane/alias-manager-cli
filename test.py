#!/usr/bin/env python

from __future__ import print_function

from configobj import ConfigObj
from validate import Validator
from ConfigParser import SafeConfigParser
from pprint import pprint

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

# CONFIGSPEC = """
# [database]
# host = string(default=None)
# dbname = string(default=None)
# table = string(default=None)
# user = string(default=None)
# password = string(default=None)

# [add]
# digits = int(default=0)
# target = string(default=None)
# """
CONFIGSPEC = [
    '[database]',
    'host = string(default=None)',
    #'dbname = string(default=None)',
    'dbname = string',
    'table = string(default=None)',
    'user = string(default=None)',
    'password = string(default=None)',
    '',
    '[add]',
    'digits = integer(min=0, default=0)',
    'target = string(default=None)',
    ]

def config_dict(config):
    ret = {}
    for section in config.sections():
        ret[section] = {}
        for option, value in config.items(section):
            ret[section][option] = value
    return ret

def init_config(config):
    for section in DEFAULT_CONFIG.keys():
        if not config.has_section(section):
            config.add_section(section)
        for option, value in DEFAULT_CONFIG[section].items():
            config.set(section, option, str(value))

def main():
    # config = SafeConfigParser()
    # init_config(config)
    # config.read('alias-manager.conf')
    # pprint(config_dict(config))
    config = ConfigObj('alias-manager.conf', configspec=CONFIGSPEC, stringify=True)
    val = Validator()
    pprint(config.validate(val))
    pprint(dict(config))

if __name__ == '__main__':
    main()

