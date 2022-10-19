# ISC DHCP NetBox

Updates NetBox with ISC DHCP lease information.

## Installation

TODO: Complete install instructions.

## Pre-requisites

### ipam / ip-addresses

The program will automatically create IP address objects for the DHCP managed IP range.

Make sure to set the status to **DHCP** on all DHCP controlled IP addresses (should they already be existing).

### other / tags

The IP addresses under control of this program are being tagged.

Create the **live-data** tag in NetBox prior to running this program.

| Key  | Value     |
| ---  | ---       |
| Name | Live Data |
| Slug | live-data |

## Configuration

### dhcp_netbox.conf

The configuration file can be stored in any of the below locations.

* The current working directory of the script
* The home directory of the current user
* In **/etc/isc_dhcp_netbox** directory (create the directory manually)
* In a path specified in environment variable: **ISC_DHCP_NETBOX_CONF**

> Make sure that you always name the configuration file: **dhcp_netbox.conf**
