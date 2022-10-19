#!/usr/bin/env python3

import logging
import os
import configparser
import re

def load_config():
    ''' Load the dhcp_netbox.conf file '''
    cfg = configparser.ConfigParser()
    cfg_file = 'dhcp_netbox.conf'
    cfg_paths = [
        '{}/{}'.format(os.curdir, cfg_file), 
        '{}/{}'.format(os.path.expanduser("~"), cfg_file), 
        '/etc/isc_dhcp_netbox/{}'.format(cfg_file), 
        '{}/{}'.format(os.environ.get('ISC_DHCP_NETBOX_CONF'),cfg_file)
        ]
    #cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dhcp_netbox.conf')
    if cfg.read(cfg_paths) == []:
        raise Exception('Could not read dhcp_netbox.conf configuration file.')
    assert validate_config(cfg) is True        
    return cfg

def validate_config(cfg):
    ''' Validate our configuration settings '''
    if 'DHCP' not in cfg: raise Exception('Missing <DHCP> section in configuration.')
    if 'NetBox' not in cfg: raise Exception('Missing <NetBox> section in configuration.')
    if 'Logger' not in cfg: raise Exception('Missing <Logger> section in configuration.')

    ''' Check DHCP section '''
    expected_params = ['leases_file']
    for p in expected_params:
        if p not in cfg['DHCP']: raise Exception('Missing <{}> directive in configuration file.'.format(p))        
        if cfg['DHCP'][p] == '': raise Exception('Parameter <{}> cannot be empty.'.format(p))

    ''' Check NetBox section '''
    expected_params = ['host', 'protocol', 'api_token', 'private_key_file']
    allowed_protocols = ['http', 'https']
    for p in expected_params:
        if p not in cfg['NetBox']: raise Exception('Missing <{}> directive in configuration file.'.format(p))
    if cfg['NetBox']['protocol'] not in allowed_protocols: raise Exception('Invalid <protocol> value. Use: http or https')

    ''' Check Logger section '''
    expected_params = ['logfilepath', 'logfilename', 'loglevel']
    allowed_loglevel = ['debug', 'info', 'warning', 'error', 'critical']
    for p in expected_params:
        if p not in cfg['Logger']: raise Exception('Missing <{}> directive in configuration file.'.format(p))
        if cfg['Logger'][p] == '': raise Exception('Parameter <{}> cannot be empty.'.format(p))
    if cfg['Logger']['loglevel'].lower() not in allowed_loglevel: raise Exception('Invalid <loglevel> value: {}. Choose from: {}'.format(cfg['Logger']['loglevel'], allowed_loglevel))
    
    return True

def get_log_level(cfg):
    ''' Get the correct log level '''
    cfg_lvl = cfg['Logger']['loglevel'].upper()
    lvl = logging.NOTSET
    if cfg_lvl == 'DEBUG': lvl = logging.DEBUG
    elif cfg_lvl == 'INFO': lvl = logging.INFO
    elif cfg_lvl == 'WARNING': lvl = logging.WARNING
    elif cfg_lvl == 'ERROR': lvl = logging.ERROR
    elif cfg_lvl == 'CRITICAL': lvl = logging.CRITICAL
    return lvl

def get_leases_file_path():
    cfg = load_config()
    return cfg['DHCP']['leases_file']

def valid_ip(ip):
    ''' Simple IPv4 IP syntax validation '''
    if bool(re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)): return True
    return False