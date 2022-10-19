#!/usr/bin/env python3
import requests

""" Disable invalid SSL certificate warnings (if desired). """
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

from isc_dhcp_leases import Lease, IscDhcpLeases

leases = IscDhcpLeases('/var/lib/dhcp/dhcpd.leases')
netbox_host = 'netbox.mgmt.tobo.lan'
netbox_api_token = 'f848f83493dc5d706a416f6ad5ad485c7439ff74'

#leases.get()  # Returns the leases as a list of Lease objects
active_leases = leases.get_current()  # Returns only the currently valid dhcp leases as dict

def nb_query(req, req_type, payload=None):
    url = 'https://{}/api/'.format(netbox_host)
    req_type = req_type.upper()
    headers = {}
    if req_type == "DELETE":
        headers["Content-Type"] = "application/json;"
    headers["authorization"] = "Token {}".format(netbox_api_token)
    if req_type == 'GET':
        headers['accept'] = "application/json;"
        r = requests.get(url + req, verify=False, headers=headers)
    elif req_type == 'POST':
        r = requests.post(url + req, verify=False, headers=headers, json=payload)
    elif req_type == 'PUT':
        r = requests.put(url + req, verify=False, headers=headers, json=payload)
    elif req_type == 'PATCH':
        r = requests.patch(url + req, verify=False, headers=headers, json=payload)
    if r.ok:
        return r
    print(r.content)
    raise Exception('API call has failed.')

def nb_get(req):
    return nb_query(req, 'GET')

def nb_post(req, payload):
    return nb_query(req, 'POST', payload)

def nb_put(req, payload):
    return nb_query(req, 'PUT', payload)

def nb_patch(req, payload):
    return nb_query(req, 'PATCH', payload)

def get_nb_device(shortname=None):
    if shortname:
        """ Get current device """
        r = nb_get('dcim/devices?name={}'.format(netbox_host,shortname))
    else:
        """ Get all devices """
        r = nb_get('dcim/devices'.format(netbox_host))
    return r

def get_nb_interface(mac=None):
    if mac:
        r = nb_get('dcim/interfaces?mac_address={}'.format(str(mac.upper())))
    else:
        r = nb_get('dcim/interfaces')
    return r

def get_nb_ip(ip):
    if ip:
        r = nb_get('ipam/ip-addresses?address={}'.format(str(ip)))
    else:
        r = nb_get('ipam/ip-addresses')
    return r

def assign_interface_ip(ip_id, iface_id):
    req_url = 'ipam/ip-addresses/{}/'.format(int(ip_id))
    body = {'assigned_object_type': 'dcim.interface'}
    body['assigned_object_id'] = iface_id
    r = nb_patch(req_url, body)
    return r

def unassign_interface_ip(ip_id):
    req_url = 'ipam/ip-addresses/{}/'.format(int(ip_id))
    body = {'assigned_object_type': 'null'}
    body['assigned_object_id'] = 'null'
    r = nb_patch(req_url, body)
    return r

def assign_device_primary_ip(ip_id, device_id):
    req_url = 'dcim/devices/{}/'.format(int(device_id))
    body = {'primary_ip4': ip_id }
    r = nb_patch(req_url, body)
    return r

def unassign_device_primary_ip(device_id):
    return assign_device_primary_ip('null', device_id)

""" Get references to tags, etc. """
r = nb_get('extras/tags?slug=dhcp').json()
dhcp_tag = {'slug': r['results'][0]['slug']}
r = nb_get('extras/tags?slug=live-data').json()
live_tag = {'slug': r['results'][0]['slug']}

for lease in active_leases:
    print("Processing: {}".format(str(lease)))
    lease_obj = active_leases[lease]
    lease_ip = lease_obj.ip
    lease_binding_state = lease_obj.binding_state

    """ Get IP from netbox if existing or create if not existing. """
    r = get_nb_ip('{}/24'.format(lease_ip))
    res = r.json()
    if res['count'] == 0:
        """ IP does not exist. Create in netbox. """
        body = {'address': '{}/24'.format(lease_ip)}
        body['status'] = 'dhcp'
        body['role'] = 'loopback'
        body['dns_name'] = ''
        body['description'] = 'DHCP assigned IP'
        body['tags'] = [{'slug': 'live-data'}]
        post_res = nb_post('ipam/ip-addresses/', body)
        print("NetBox IP does not exist for current lease. Creating...")
        post_ip = post_res.json()
    else:
        post_ip = res['results'][0]
    nb_ip = post_ip

    """ Get interface from netbox if existing. """
    r = get_nb_interface(lease)
    res = r.json()
    if res['count'] > 0:
        iface = res['results'][0]
        print("Found NetBox device interface for MAC.")
        name = iface['name']
        ifid = iface['id']
        device = iface['device']['id']
        iftype = iface['type']['value']
        upd_req = 'dcim/interfaces/{}/'.format(ifid)
        """ Update tags """
        tags = iface['tags']
        tags_update = []
        set_dhcp = True
        set_live = True
        update = False
        for tag in tags:
            if 'dhcp' == tag['slug']:
                set_dhcp = False
                tags_update.append(dhcp_tag)
            if 'live-data' == tag['slug']:
                set_live = False
                tags_update.append(live_tag)
        if set_dhcp:
            tags_update.append(dhcp_tag)
            update = True
        if set_live:
            tags_update.append(live_tag)
            update = True
        if update:
            body = {'tags': tags_update}
            print("Updating interface tags...")
            upd_res = nb_patch(upd_req, body)
        """ Assign IP to interface. """
        if nb_ip['assigned_object_type'] is None and nb_ip['assigned_object_id'] is None:
            assign_res = assign_interface_ip(nb_ip['id'], ifid)
            print("Assign IP to interface.")
            primary_res = assign_device_primary_ip(nb_ip['id'], device)
            print("Assigned device primary IP.")
        else:
            if nb_ip['assigned_object_id'] == ifid:
                print("IP already assigned to interface. Skipping...")
                nb_device_raw = nb_get('dcim/devices/{}/'.format(device))
                nb_device = nb_device_raw.json()
                if nb_device['primary_ip4'] is None:
                    dassign_res = assign_device_primary_ip(nb_ip['id'],nb_device['id'])
                    print("Assigning device primary IP.")
            else:
                device_res = unassign_device_primary_ip(device)
                print("Unassign device primary IP.")
                ua_res = unassign_interface_ip(nb_ip['id'])
                print("Unassign old IP from interface.")
                assign_res = assign_interface_ip(nb_ip['id'], ifid)
                print("Assign IP to interface.")
                dassign_res = assign_device_primary_ip(nb_ip['id'], device)


#devices = get_nb_device()
#print(devices.text)

#one_device = get_nb_device('apc')
#print(one_device.text)
