from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class MemoryClass(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CANONICAL = "canonical"
    PROCEDURAL = "procedural"

class AdmissionState(str, Enum):
    EPHEMERAL = "EPHEMERAL"
    EPISODIC = "EPISODIC"
    SEMANTIC_CANDIDATE = "SEMANTIC_CANDIDATE"
    SEMANTIC = "SEMANTIC"
    CANONICAL_CANDIDATE = "CANONICAL_CANDIDATE"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"

class HealthState(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    CONFLICTED = "CONFLICTED"
    QUARANTINED = "QUARANTINED"
    RECOVERY = "RECOVERY"
    HALTED = "HALTED"

class Authority(int, Enum):
    A0 = 0
    A1 = 1
    A2 = 2
    A3 = 3
    A4 = 4
    A5 = 5

@dataclass(frozen=True)
class MemoryRecord:
    content: Any
    memory_class: MemoryClass
    source: str
    timestamp: str
    confidence: float | None = None
    scope: str | None = None
    integrity_hash: str | None = None
    admission: AdmissionState = AdmissionState.EPHEMERAL

@dataclass(frozen=True)
class EffectIntent:
    intent: str
    actor: str
    target: str
    required_authority: Authority
    operation: str
    metadata: dict[str, Any] = field(default_factory=dict)
