""" Utils module of package isc_dhcp_netbox """
import logging
import os
import configparser
import re

def load_config(cfg_file: str ='dhcp_netbox.conf') -> dict:
    """
    Searches and loads the dhcp_netbox.conf file.

    :return: A config dictionary as returned by configparser.
    :rtype: dict
    """
    print(os.environ.get('ISC_DHCP_NETBOX_CONF'))
    cfg = configparser.ConfigParser()
    cfg_paths = [
        f"{os.curdir}/{cfg_file}",
        '{}/{}'.format(os.path.expanduser("~"), cfg_file), 
        f"/etc/isc_dhcp_netbox/{cfg_file}",
        '{}/{}'.format(os.environ.get('ISC_DHCP_NETBOX_CONF'),cfg_file)
        ]
    if not cfg.read(cfg_paths):
        raise FileNotFoundError(f"Could not read {cfg_file} configuration file.")
    assert validate_config(cfg) is True
    return cfg

def validate_config(cfg):
    ''' 
    Basic validation of the configuration file settings.
           
    :param cfg: A config dictionary as returned by configparser.
    :type cfg: dict
    :raises ValueError: Missing <x> section in configuration.
    :raises ValueError: Missing <x> directive in configuration file.
    :raises ValueError: Parameter <x> cannot be empty.
    :raises ValueError: Invalid <protocol> value. Use: http or https.
    :raises ValueError: Invalid <loglevel> value: <x>. Choose from: ...
    :return: True on success
    :rtype: bool
    '''
    if 'DHCP' not in cfg:
        raise ValueError('Missing <DHCP> section in configuration.')
    if 'NetBox' not in cfg:
        raise ValueError('Missing <NetBox> section in configuration.')
    if 'Logger' not in cfg:
        raise ValueError('Missing <Logger> section in configuration.')

    # Check DHCP section
    expected_params = ['leases_file']
    for p in expected_params:
        if p not in cfg['DHCP']:
            raise ValueError(f"Missing <{p}> directive in configuration file.")
        if cfg['DHCP'][p] == '':
            raise ValueError(f"Parameter <{p}> cannot be empty.")

    # Check NetBox section
    expected_params = ['host', 'protocol', 'api_token', 'private_key_file']
    allowed_protocols = ['http', 'https']
    for p in expected_params:
        if p not in cfg['NetBox']:
            raise ValueError(f"Missing <{p}> directive in configuration file.")
    if cfg['NetBox']['protocol'] not in allowed_protocols:
        raise ValueError('Invalid <protocol> value. Use: http or https')

    # Check Logger section
    expected_params = ['logfilepath', 'logfilename', 'loglevel']
    allowed_loglevel = ['debug', 'info', 'warning', 'error', 'critical']
    for p in expected_params:
        if p not in cfg['Logger']:
            raise ValueError(f"Missing <{p}> directive in configuration file.")
        if cfg['Logger'][p] == '':
            raise ValueError(f"Parameter <{p}> cannot be empty.")
    current_loglevel = cfg['Logger']['loglevel']
    if current_loglevel.lower() not in allowed_loglevel:
        raise ValueError(f"Invalid <loglevel> value: {current_loglevel}. Choose from: {allowed_loglevel}")
    return True

def get_log_level(cfg: dict) -> int:
    ''' 
    Get the correct log level 
    
    :param cfg: A config dictionary as returned by configparser.
    :type cfg: dict
    :return: The numeric log level based on the setting in the configuration file.
    :rtype: int
    '''
    cfg_lvl = cfg['Logger']['loglevel'].upper()
    lvl = logging.NOTSET
    if cfg_lvl == 'DEBUG':
        lvl = logging.DEBUG
    elif cfg_lvl == 'INFO':
        lvl = logging.INFO
    elif cfg_lvl == 'WARNING':
        lvl = logging.WARNING
    elif cfg_lvl == 'ERROR':
        lvl = logging.ERROR
    elif cfg_lvl == 'CRITICAL':
        lvl = logging.CRITICAL
    return int(lvl)

def get_leases_file_path():
    '''
    Reads the path to the DHCP leases file from the configuration.

    :raises FileNotFoundError: Path to DHCP lease file does not exist.
    :return: A string holding the path to the DHCP leases file.
    :rtype: str
    '''
    cfg = load_config()
    path = cfg['DHCP']['leases_file']
    if os.path.exists(path):
        return path
    raise FileNotFoundError('Path to DHCP lease file does not exist.')

def valid_ip(ip):
    ''' 
    Simple IPv4 IP syntax validation.

    :param ip: An IP address in format: xxx.xxx.xxx.xxx
    :type ip: string
    :return: True or False depending if IP is valid or not
    :rtype: bool
    '''
    if bool(re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)):
        for p in ip.split('.'):
            if int(p) < 0 or int(p) > 255:
                return False
        return True
    return False
