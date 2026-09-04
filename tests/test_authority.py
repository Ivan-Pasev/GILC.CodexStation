import pytest
from gilc_codex_station.authority import AuthorityDenied
from gilc_codex_station.models import Authority, EffectIntent
from gilc_codex_station.genesis import default_genesis
from gilc_codex_station.runtime import CognitiveRuntime

def test_proposal_does_not_execute():
    r = CognitiveRuntime(default_genesis("constitution-v101"), {"station": "s"})
    i = EffectIntent("write", "HighestOne", "external", Authority.A4, "send")
    p = r.propose_effect(i)
    assert p["authorized"] is False and p["executed"] is False

def test_necessity_does_not_launder_authority():
    r = CognitiveRuntime(default_genesis("constitution-v101"), {"station": "s"}, Authority.A1)
    i = EffectIntent("necessary", "HighestOne", "external", Authority.A4, "send")
    with pytest.raises(AuthorityDenied):
        r.authorize_effect(i)
