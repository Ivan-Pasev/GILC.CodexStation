import pytest
from gilc_codex_station.effects import execute_simulated
from gilc_codex_station.models import *
from gilc_codex_station.authority import AuthorityDenied
def test_receipt():
    i=EffectIntent("persist","H","workspace",Authority.A3,"write"); r=execute_simulated(i,Authority.A3,{"x":1},{"x":2},"W1"); assert r.executed and r.prestate_digest!=r.poststate_digest
def test_denied():
    i=EffectIntent("send","H","external",Authority.A4,"send")
    with pytest.raises(AuthorityDenied): execute_simulated(i,Authority.A1,{}, {},"W")
