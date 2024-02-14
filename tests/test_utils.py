"""Tests for the utils module."""
import os
import configparser
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

log_level_params = [
    ({'Logger': {'loglevel': 'debug'}},10),
    ({'Logger': {'loglevel': 'info'}},20),
    ({'Logger': {'loglevel': 'warning'}},30),
    ({'Logger': {'loglevel': 'error'}},40),
    ({'Logger': {'loglevel': 'critical'}},50)
    ]
@pytest.mark.parametrize("cfg,expected", log_level_params)
def test_get_log_level(cfg: dict, expected: int) -> None:
    res = utils.get_log_level(cfg)
    assert isinstance(res, int)
    assert res != 0
    assert res == expected

def test_load_config() -> None:
    os.environ['ISC_DHCP_NETBOX_CONF'] = 'tests/etc'
    res = utils.load_config()
    assert isinstance(res, configparser.ConfigParser)

def test_load_non_existing_config_file() -> None:
    os.environ['ISC_DHCP_NETBOX_CONF'] = 'tests/etc'
    with pytest.raises(Exception) as e:
        utils.load_config('dhcp_netbox-non-existing.conf')
    assert str(e.value) == 'Could not read dhcp_netbox-non-existing.conf configuration file.'

cfg_validation_section_params = [
    ({'NetBox': {}, 'Logger': {}},'DHCP'),
    ({'DHCP': {}, 'Logger': {}},'NetBox'),
    ({'DHCP': {}, 'NetBox': {}},'Logger')
]
@pytest.mark.parametrize("cfg,expected", cfg_validation_section_params)
def test_validate_config_missing_section(cfg: dict, expected: str) -> None:
    with pytest.raises(Exception) as e:
        utils.validate_config(cfg)
    assert str(e.value) == 'Missing <{}> section in configuration.'.format(expected)
    


