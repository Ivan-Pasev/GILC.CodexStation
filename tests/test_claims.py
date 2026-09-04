from gilc_codex_station.claims import *
def test_hypothesis_not_truth(): assert not Claim("X",ClaimDomain.WORLD,EpistemicStatus.HYPOTHESIS,"model").assert_world_truth()
def test_unknown_preserved(): assert Claim("X",ClaimDomain.WORLD,EpistemicStatus.UNKNOWN).status is EpistemicStatus.UNKNOWN
