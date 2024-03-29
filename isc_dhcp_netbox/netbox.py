""" Netbox module of package isc_dhcp_netbox """
import logging
import pynetbox
from isc_dhcp_netbox import utils

def netbox_session(cfg: dict):
    '''
    Creates the pynetbox session object.

    :param cfg: A config dictionary as returned by configparser.
    :type cfg: dict
    :return: A :class:`pynetbox.core.api.Api` object.
    :rtype: pynetbox.core.api.Api
    '''
    proto = cfg['NetBox']['protocol']
    host = cfg['NetBox']['host']
    token = cfg['NetBox']['api_token']
    url = f"{proto.lower()}://{host}"
    nb = pynetbox.api(url, token=token)
    logging.debug('Started NetBox session.')
    return nb

def get_ip_prefix(nb, ip: str) -> int:
    ''' 
    Searches NetBox for the parent prefix of a given IP and returns the CIDR netmask.
    
    :param nb: A handle to the :class:`pynetbox.core.api.Api` object
    :type nb: pynetbox.core.api.Api
    :param ip: The IP for which we retrieve the parent network and prefix
    :type ip: str
    :raises ValueError: Could not derive prefix of <IP>
    :return: an integer representing the CIDR netmask (0-32)
    :rtype: int
    '''
    assert utils.valid_ip(ip)
    nb_ip_prefix = nb.ipam.prefixes.filter(contains=ip, children=0)
    if len(nb_ip_prefix) != 1:
        raise ValueError(f"Could not derive prefix of {ip}")
    for pfx in nb_ip_prefix:
        out = str(pfx).split('/',1)
    return int(out[1])

def get_ip_by_address(nb, ip: str):
    ''' 
    Searches for a given IP in NetBox.
    
    :param nb: A handle to the :class:`pynetbox.core.api.Api` object
    :type nb: pynetbox.core.api.Api
    :param ip: The IP we want to retrieve from NetBox
    :type ip: str
    :return: A NetBox :class:`pynetbox.models.ipam.IpAddresses` object.
    :rtype: pynetbox.models.ipam.IpAddresses    
    '''
    return nb.ipam.ip_addresses.get(address=ip)

def get_interface_by_mac(nb, mac: str):
    '''
    Search for a device interface that uses the given MAC.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object
    :type nb: pynetbox.core.api.Api
    :param mac: The MAC for which we try to find an interface in NetBox.
    :type mac: str
    :return: A NetBox :class:`pynetbox.models.dcim.Interfaces` object or None if nothing was found
    :rtype: pynetbox.models.dcim.Interfaces or None
    '''
    out = None
    nb_interface = nb.dcim.interfaces.filter(mac_address=mac)
    if len(nb_interface) == 1:
        for ifc in nb_interface:
            out = ifc
    return out

def get_interface_by_id(nb, interface_id: int):
    '''
    Search for a device interface that uses the given ID.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object
    :type nb: pynetbox.core.api.Api
    :param interface_id: The ID of the interface.
    :type interface_id: int
    :return: A NetBox :class:`pynetbox.models.dcim.Interfaces` object or None if nothing was found
    :rtype: pynetbox.models.dcim.Interfaces or None
    '''
    out = None
    nb_interface = nb.dcim.interfaces.filter(id=interface_id)
    if len(nb_interface) == 1:
        for ifc in nb_interface:
            out = ifc
    return out

def create_ip(nb, ip: str):
    '''
    This creates a new IP object in NetBox.
    
    :param nb: A handle to the :class:`pynetbox.core.api.Api` object.
    :type nb: pynetbox.core.api.Api
    :param ip: The IP in NetBox format: xxx.xxx.xxx.xxx/zz
    :type ip: str
    :return: A NetBox :class:`pynetbox.models.ipam.IpAddresses` object.
    :rtype: pynetbox.models.ipam.IpAddresses    
    '''
    nb_ip = nb.ipam.ip_addresses.create({
                'address': ip,
                'status': 'dhcp',
                'role': 'loopback',
                'dns_name': '',
                'description': 'DHCP assigned and managed IP address',
                'tags': [{'slug': 'live-data'}]
                })
    return nb_ip

def assign_interface_ip(ip_obj, interface_id: int):
    '''
    This assigns an IP to a given interface ID.

    :param ip_obj: A handle to the :class:`pynetbox.models.ipam.IpAddresses` object
    :type ip_obj: pynetbox.models.ipam.IpAddresses
    :param interface_id: The ID of the interface the IP should get assigned to.
    :type interface_id: int
    :return: Changed NetBox interface object
    :rtype: :class:`pynetbox.models.ipam.IpAddresses` object
    '''
    ip_obj.assigned_object_id = interface_id
    ip_obj.assigned_object_type = 'dcim.interface'
    ip_obj.save()
    return ip_obj

def unassign_interface_ip(nb, ip_obj):
    '''
    This un-assigns an IP from an interface.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object.
    :type nb: pynetbox.core.api.Api
    :param ip_obj: A handle to the :class:`pynetbox.models.ipam.IpAddresses` object
    :type ip_obj: object
    :return: Changed NetBox IP address object
    :rtype: :class:`pynetbox.models.ipam.IpAddresses` object
    '''
    unset_device_primary_ip(nb, ip_obj)
    ip_obj.assigned_object_id = None
    ip_obj.assigned_object_type = None
    ip_obj.save()
    return ip_obj

def get_device_by_id(nb, device_id: int):
    '''
    Retrieves a device object by device ID from NetBox.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object.
    :type nb: pynetbox.core.api.Api
    :param device_id: An integer representing the device ID in NetBox
    :type device_id: int
    :return: The retrieved Device object
    :rtype: :class:`pynetbox.models.dcim.Devices` object
    '''
    device_results = nb.dcim.devices.filter(id=device_id, exclude="config_context")
    if len(device_results) == 1:
        for d in device_results:
            return d

def set_device_primary_ip(nb, device_id, ip_id: int):
    '''
    Set the primary IPv4 address for the given device in NetBox.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object.
    :type nb: pynetbox.core.api.Api
    :param device_id: An integer representing the device ID in NetBox
    :type device_id: int
    :param ip_id: The ID of the IP address to be assigned to the device.
    :type ip_id: int
    TODO: add checks and return value...
    '''
    d = get_device_by_id(nb, device_id)
    d.primary_ip4 = ip_id
    d.save()

def unset_device_primary_ip(nb, ip_obj):
    '''
    An alias for the set_device_primary_ip function that allows you to un-assign
    a given IP address from the device primary IP field.

    :param nb: A handle to the :class:`pynetbox.core.api.Api` object.
    :type nb: pynetbox.core.api.Api
    :param ip_obj: A :class:`pynetbox.models.ipam.IpAddresses` object
    :type ip_obj: pynetbox.models.ipam.IpAddresses
    TODO: add checks and return value...
    '''
    if ip_obj.assigned_object_type == 'dcim.interface':
        iface = get_interface_by_id(nb, ip_obj.assigned_object_id)
        set_device_primary_ip(nb, iface.device.id, None)
