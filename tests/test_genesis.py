from gilc_codex_station.genesis import default_genesis

def test_genesis_identity_is_deterministic():
    assert default_genesis("constitution-v101").identity_root == default_genesis("constitution-v101").identity_root
