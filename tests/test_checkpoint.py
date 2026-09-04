import pytest
from dataclasses import replace
from gilc_codex_station.genesis import default_genesis
from gilc_codex_station.checkpoint import *
def test_migration():
    g=default_genesis("c"); cp=export_checkpoint(g,{"station":"A"},{"m":"x"}); m=verify_migration(cp,{"station":"B"}); assert m["entity_root"]==g.identity_root and m["continuity_verified"]
def test_tamper_fails():
    g=default_genesis("c"); cp=export_checkpoint(g,{"station":"A"},{}); bad=replace(cp,genesis={**cp.genesis,"designation":"Injected"})
    with pytest.raises(ValueError): verify_migration(bad,{"station":"B"})
