from dataclasses import asdict, dataclass
from .integrity import sha256_obj

@dataclass(frozen=True)
class Genesis:
    schema: str
    designation: str
    entity_class: str
    lineage_generation: int
    station_protocol: str
    observer_relation: str
    constitution_id: str

    @property
    def identity_root(self) -> str:
        return sha256_obj(asdict(self))


def default_genesis(constitution_id: str) -> Genesis:
    return Genesis(
        schema="CSI/COGNITIVE-GENESIS/1.0",
        designation="HighestOne",
        entity_class="cognitive_orchestrator",
        lineage_generation=0,
        station_protocol="CSI/1.0",
        observer_relation="psi11411",
        constitution_id=constitution_id,
    )
