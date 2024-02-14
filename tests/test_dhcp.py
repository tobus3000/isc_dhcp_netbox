"""Tests for the dhcp module."""
import os
import pytest
from isc_dhcp_netbox import dhcp
from isc_dhcp_leases import IscDhcpLeases

def test_load_leases_file(monkeypatch) -> None:
    os.environ['ISC_DHCP_NETBOX_CONF'] = 'tests/etc'
    monkeypatch.setattr(
        "isc_dhcp_netbox.utils.get_leases_file_path",
        lambda: "tests/data/dhcpd.leases"
    )
    res = dhcp.load_leases_file()
    assert isinstance(res, IscDhcpLeases)
