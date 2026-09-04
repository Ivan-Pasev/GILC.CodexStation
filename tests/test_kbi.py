import pytest
from gilc_codex_station.kbi import *
def test_kbi_failure():
    r=evaluate({"a":"A1"},[Invariant("I",lambda c:c["a"]=="A0","A0 required")])
    with pytest.raises(ValueError): require_all(r)
