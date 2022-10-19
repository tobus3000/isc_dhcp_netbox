# ISC DHCP NetBox

Updates NetBox with ISC DHCP lease information.

## Overview

This program lets you synchronize NetBox with your ISC DHCP server.

### Active Leases

Activities on active leases.

* Create new IP address if not already existing.
* Assign IP address to interface if lease MAC matches the interface MAC.
* Assign IP as primary IPv4 address on the device the interface belongs to.
* Re-assign IP from interface 1 to interface 2 should the DHCP lease be handed out to another device.

### Inactive/Expired Leases

Activities on inactive and/or expired leases.

* The device primary IP will be set to None.
* The interface assignments will be removed from the IP.

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

* Current working directory of the script
* Home directory of the current user
* **/etc/isc_dhcp_netbox** directory (create the directory manually)
* Path specified in environment variable: **ISC_DHCP_NETBOX_CONF**

> Make sure to always name the configuration file: **dhcp_netbox.conf**
