from dataclasses import asdict, dataclass
from .authority import authorize
from .genesis import Genesis
from .integrity import sha256_obj
from .models import Authority, EffectIntent, HealthState, MemoryRecord
from .memory import admit

@dataclass
class CognitiveRuntime:
    genesis: Genesis
    station_descriptor: dict
    granted_authority: Authority = Authority.A1
    health: HealthState = HealthState.NOMINAL

    @property
    def entity_root(self) -> str:
        return self.genesis.identity_root

    @property
    def station_root(self) -> str:
        return sha256_obj(self.station_descriptor)

    def admit_memory(self, record: MemoryRecord) -> MemoryRecord:
        return admit(record)

    def propose_effect(self, intent: EffectIntent) -> dict:
        return {"intent": asdict(intent), "authorized": False, "executed": False}

    def authorize_effect(self, intent: EffectIntent) -> bool:
        return authorize(intent, self.granted_authority)

    def homeostasis(self) -> dict:
        separated = self.station_root != self.entity_root
        return {
            "identity_integrity": True,
            "station_entity_separation": separated,
            "health": self.health.value if separated else HealthState.QUARANTINED.value,
        }
