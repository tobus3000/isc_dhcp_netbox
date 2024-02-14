""" Main module of package isc_dhcp_netbox """
import sys
import logging
from isc_dhcp_netbox import utils
from isc_dhcp_netbox import netbox
from isc_dhcp_netbox import dhcp

def main():
    ''' Load and validate configuration file '''
    try:
        cfg = utils.load_config()
    except FileNotFoundError as exc:
        print(str(exc))
        raise FileNotFoundError from exc

    # Start logging
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        filename='{}/{}'.format(cfg['Logger']['logfilepath'],cfg['Logger']['logfilename']),
        level=utils.get_log_level(cfg)
        )
    logging.info('Starting dhcp_netbox sync...')

    # Get a pynetbox object
    nb = netbox.netbox_session(cfg)

    # Get all DHCP managed IPs from NetBox
    dhcp_ips = []
    for ip in nb.ipam.ip_addresses.filter(status='dhcp'):
        dhcp_ips.append(ip.address)
    logging.debug("DHCP managed IPs in NetBox: %s", len(dhcp_ips))

    # Process active leases
    active_leases = dhcp.get_active_leases()
    logging.debug("Active leases: %s", len(active_leases))
    for mac in active_leases:
        lease = active_leases[mac]
        logging.info("Processing %s - %s",mac, lease.ip)

        # Identify the netmask of our lease IP
        try:
            nb_ip_prefix = netbox.get_ip_prefix(nb, lease.ip)
        except ValueError:
            # Failed to derive prefix from given IP.
            # TODO: fix...
            pass

        # Check if NetBox already has an IP object that matches the lease IP.
        nb_ip = netbox.get_ip_by_address(nb, f"{lease.ip}/{nb_ip_prefix}")
        if nb_ip is None: 
            # If no IP is found, we create a new one and set the defaults.
            nb_ip = netbox.create_ip(nb, f"{lease.ip}/{nb_ip_prefix}")
        else:
            dhcp_ips.remove(nb_ip.address)

        logging.debug("Interface association: %s", nb_ip.assigned_object)

        # Check if a device interface can be found for the lease MAC.
        nb_interface = netbox.get_interface_by_mac(nb, mac)
        logging.debug("Found interface for MAC: %s", nb_interface)

        if nb_ip.assigned_object is None and nb_interface is not None:
            logging.debug("Assigning interface %s to IP %s", nb_interface, lease.ip)
            nb_ip = netbox.assign_interface_ip(nb_ip, nb_interface.id)
            logging.debug("Interface belongs to device: %s", nb_interface.device.name)
            nb_primary_ip = netbox.set_device_primary_ip(nb, nb_interface.device.id, nb_ip.id)

        elif nb_ip.assigned_object is not None and nb_interface is not None:
            if nb_ip.assigned_object_id == nb_interface.id:
                logging.debug("Assigned Interface is unchanged.")
            else:
                logging.debug(
                    "Changing interface assignment (%s) for IP %s",
                    nb_interface,
                    lease.ip
                )
                nb_ip = netbox.assign_interface_ip(nb_ip, nb_interface.id)
                nb_primary_ip = netbox.set_device_primary_ip(nb, nb_interface.device.id, nb_ip.id)

    # Process expired/inactive leases
    for ip in dhcp_ips:
        logging.info("Deleting interface assignement for %s", ip)
        nb_ip = netbox.get_ip_by_address(nb, ip)
        if nb_ip.assigned_object is not None:
            netbox.unassign_interface_ip(nb, nb_ip)
    logging.info("DHCP Lease sync has completed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exit(e)
