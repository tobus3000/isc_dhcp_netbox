"""Tests for the netbox module."""
import os
import ssl
import pytest
import pynetbox
from isc_dhcp_netbox import netbox

test_cfg = {
    "NetBox": {
        "protocol":"https",
        "host":"",
        "api_token": ""
    }
}

def test_netbox_session() -> None:
    nb = netbox.netbox_session(test_cfg)
    assert isinstance(nb, pynetbox.core.api.Api)

@pytest.mark.parametrize(
        "ip", [
            ('192.168.200.1',24),
            ('10.10.10.2',24),
            ('10.10.11.0',25),
            ('10.10.11.128',25)
        ]
)
def test_get_ip_prefix(ip: tuple) -> None:
    nb = netbox.netbox_session(test_cfg)
    nb.http_session.verify=False
    nb_ip_prefix = netbox.get_ip_prefix(nb, ip[0])
    assert nb_ip_prefix == ip[1]
