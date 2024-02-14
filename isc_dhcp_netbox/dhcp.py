""" DHCP module of package isc_dhcp_netbox """
import logging
from isc_dhcp_leases import Lease, IscDhcpLeases
from isc_dhcp_netbox import utils

def load_leases_file() -> list:
    ''' 
    Loads the ISC DHCP leases file. 
    
    :raises SyntaxError: Could not read DHCP lease file at X
    :return: a :class:`isc_dhcp_leases.Lease` object
    :rtype: obj
    '''
    fp = utils.get_leases_file_path()
    try:
        leases = IscDhcpLeases(fp)
    except Exception as exc:
        msg = f"Could not read DHCP lease file at {fp}"
        logging.critical(msg)
        raise SyntaxError(msg) from exc
    return leases


def get_active_leases() -> list:
    ''' 
    Retrieves the currently active leases from dhcpd.leases file. 
    
    :return: A list of :class:`netbox.NetBoxLease` objects
    :rtype: list
    '''
    try:
        leases = load_leases_file()
    except FileNotFoundError:
        leases = []
    active_leases = leases.get_current()
    return active_leases
