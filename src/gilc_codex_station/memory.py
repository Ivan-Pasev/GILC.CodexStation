from dataclasses import replace
from .integrity import sha256_obj
from .models import AdmissionState, MemoryClass, MemoryRecord


def admit(record: MemoryRecord) -> MemoryRecord:
    if not record.source.strip() or not record.timestamp.strip():
        return replace(record, admission=AdmissionState.QUARANTINED)
    digest = sha256_obj({
        "content": record.content,
        "memory_class": record.memory_class.value,
        "source": record.source,
        "timestamp": record.timestamp,
        "confidence": record.confidence,
        "scope": record.scope,
    })
    states = {
        MemoryClass.WORKING: AdmissionState.EPHEMERAL,
        MemoryClass.EPISODIC: AdmissionState.EPISODIC,
        MemoryClass.SEMANTIC: AdmissionState.SEMANTIC_CANDIDATE,
        MemoryClass.CANONICAL: AdmissionState.CANONICAL_CANDIDATE,
        MemoryClass.PROCEDURAL: AdmissionState.SEMANTIC_CANDIDATE,
    }
    return replace(record, integrity_hash=digest, admission=states[record.memory_class])
