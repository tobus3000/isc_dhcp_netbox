# Changelog for isc_dhcp_netbox

## Syntax

### Entry Format

    * Author: Authors Initials
    * Change Type: See Change Type Keys
    * Description: Free form string detailing change

### Change Type Keys

    * Merged: Branch has been merged with release branch
    * Added: Feature, Function or Code added
    * Fixed: Reported issue or discovered bug fixed
    * Changed: Functionality or Feature change
    * Deleted: Code, Feature or Functionality removed

## Change History

### v0.0.2 - Bugfix Release

TODO: [Issue #4](https://github.com/tobus3000/isc_dhcp_netbox/issues/4)

### v0.0.1 - Initial Release

* *TH*: *Added*: Create new IP address in NetBox if not already existing when lease is handed out to client.
* *TH*: *Added*: Assign IP address to interface in NetBox if lease MAC matches the interface MAC.
* *TH*: *Added*: Assign IP as primary IPv4 address on the device the interface belongs to.
* *TH*: *Added*: Re-assign IP in NetBox from interface 1 to interface 2 should the DHCP lease be handed out to another device.
* *TH*: *Added*: Set device primary IP to None on lease expiry.
* *TH*: *Added*: Remove interface assignment on lease expiry.