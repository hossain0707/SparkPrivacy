import pytest
from sparkprivacy.ssh import validate_alias, profiles, TunnelManager


def test_validate_alias():
    assert validate_alias('dgx-spark.local')=='dgx-spark.local'
    with pytest.raises(ValueError):validate_alias('-oProxyCommand=sh')
    with pytest.raises(ValueError):validate_alias('host;echo hi')
    with pytest.raises(ValueError):validate_alias('')


def test_safe_config_alias_import(tmp_path):
    path=tmp_path/'config'
    path.write_text('Host my-spark another-host\n HostName 10.0.0.1\nHost *\n HostName invalid\n')
    assert profiles(path)==['another-host','my-spark']


def test_tunnel_bad_ports():
    t=TunnelManager()
    with pytest.raises(ValueError):t.start('example',0)
    with pytest.raises(ValueError):t.start('example',8000,80)
    assert t.status()==[]
