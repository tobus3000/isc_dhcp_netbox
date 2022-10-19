#!/usr/bin/env python3

from isc_dhcp_leases import Lease, IscDhcpLeases
import logging
from isc_dhcp_netbox import utils

def load_leases_file():
    ''' 
    Loads the ISC DHCP leases file. 
    
    :raises Exception: Could not read DHCP lease file at X
    :return: a :class:`isc_dhcp_leases.Lease` object
    :rtype: obj
    '''
    fp = utils.get_leases_file_path()
    try:
        leases = IscDhcpLeases(fp)
    except:
        msg = 'Could not read DHCP lease file at {}'.format(fp)
        logging.critical(msg)
        raise Exception(msg)
    return leases


def get_active_leases():
    ''' 
    Retrieves the currently active leases from dhcpd.leases file. 
    
    :return: A list of :class:`netbox.NetBoxLease` objects
    :rtype: list
    '''
    out = []
    leases = load_leases_file()
    active_leases = leases.get_current()
    return active_leases

