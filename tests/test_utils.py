#!/usr/bin/env python3

import pytest
import os
import configparser
from isc_dhcp_netbox import utils

@pytest.mark.parametrize("ip", ['192.168.200.1', '10.10.5.1', '255.255.255.255', '1.1.1.1', '10.255.128.0'])
def test_valid_ip(ip: str) -> None:
    res = utils.valid_ip(ip)
    assert res == True

@pytest.mark.parametrize("ip", ['192.168.200', '10.10.c.1', '255.255.255.256', '1..1.1', '10.2552.128.0'])
def test_invalid_ip(ip: str) -> None:
    res = utils.valid_ip(ip)
    assert res == False

log_level_params = [
    {'Logger': {'loglevel': 'info'}},
    {'Logger': {'loglevel': 'debug'}},
    {'Logger': {'loglevel': 'warning'}},
    {'Logger': {'loglevel': 'error'}},
    {'Logger': {'loglevel': 'critical'}}
    ]
@pytest.mark.parametrize("cfg", log_level_params)
def test_get_log_level(cfg: dict) -> None:
    res = utils.get_log_level(cfg)
    assert isinstance(res, int)
    assert res != 0
    assert res >= 10 and res <= 50


def test_load_config() -> None:
    os.environ['ISC_DHCP_NETBOX_CONF'] = 'tests/etc'
    res = utils.load_config()
    assert isinstance(res, configparser.ConfigParser)

def test_load_non_existing_config_file() -> None:
    os.environ['ISC_DHCP_NETBOX_CONF'] = 'tests/etc'
    with pytest.raises(Exception) as e:
        utils.load_config('dhcp_netbox-non-existing.conf')
    assert str(e.value) == 'Could not read dhcp_netbox-non-existing.conf configuration file.'
    

# cfg_path_params = [
#     {'DHCP': {'leases_file': '/tmp'}}
# ]
# @pytest.mark.parametrize("cfg", cfg_path_params)
# def test_get_leases_file_path(cfg: dict) -> None:
#     res = utils.get_leases_file_path(cfg)
#     assert isinstance(res, str)
#     assert res != ''


