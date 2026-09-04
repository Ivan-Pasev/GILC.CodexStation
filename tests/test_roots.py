from gilc_codex_station.genesis import default_genesis
from gilc_codex_station.runtime import CognitiveRuntime

def test_station_entity_roots_are_separate():
    r = CognitiveRuntime(default_genesis("constitution-v101"), {"station": "test", "release": "101.0.0a2"})
    assert r.station_root != r.entity_root
    assert r.homeostasis()["health"] == "NOMINAL"
