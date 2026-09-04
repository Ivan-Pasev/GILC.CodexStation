import pytest
from gilc_codex_station.mlco import *
def test_reconcile_one_lineage():
    w=reconcile([RoleResult(Role.ARCHITECT,"t","a","L0"),RoleResult(Role.VERIFIER,"t","v","L0")]); assert w.digest
def test_cross_lineage_denied():
    with pytest.raises(ValueError): reconcile([RoleResult(Role.ARCHITECT,"t","a","L0"),RoleResult(Role.VERIFIER,"t","v","L1")])
