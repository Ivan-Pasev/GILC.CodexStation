from gilc_codex_station.memory import admit
from gilc_codex_station.models import MemoryClass, MemoryRecord, AdmissionState

def test_canonical_memory_is_candidate():
    r = MemoryRecord({"claim": "x"}, MemoryClass.CANONICAL, "test", "2026-09-04T00:00:00Z")
    out = admit(r)
    assert out.admission is AdmissionState.CANONICAL_CANDIDATE
    assert out.integrity_hash

def test_missing_provenance_quarantines():
    r = MemoryRecord("x", MemoryClass.SEMANTIC, "", "2026-09-04T00:00:00Z")
    assert admit(r).admission is AdmissionState.QUARANTINED
