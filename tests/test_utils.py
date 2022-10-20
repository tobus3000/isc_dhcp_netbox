#!/usr/bin/env python3

import pytest
from isc_dhcp_netbox import utils

@pytest.mark.parametrize("ip", ['192.168.200.1', '10.10.5.1', '255.255.255.255', '1.1.1.1', '10.255.128.0'])
def test_valid_ip(ip: str) -> None:
    res = utils.valid_ip(ip)
    assert res == True

@pytest.mark.parametrize("ip", ['192.168.200', '10.10.c.1', '255.255.255.256', '1..1.1', '10.2552.128.0'])
def test_invalid_ip(ip: str) -> None:
    res = utils.valid_ip(ip)
    assert res == False
