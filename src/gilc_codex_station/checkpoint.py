from dataclasses import dataclass,asdict
from .integrity import sha256_obj
@dataclass(frozen=True)
class Checkpoint:
    entity_root:str;station_root:str;genesis:dict;state_digest:str
def export_checkpoint(genesis,station_descriptor,state):
    return Checkpoint(genesis.identity_root,sha256_obj(station_descriptor),asdict(genesis),sha256_obj(state))
def verify_migration(cp,target_station_descriptor):
    target=sha256_obj(target_station_descriptor)
    if target==cp.station_root: raise ValueError("migration target must differ")
    if sha256_obj(cp.genesis)!=cp.entity_root: raise ValueError("entity lineage integrity failure")
    return {"entity_root":cp.entity_root,"source_station_root":cp.station_root,"target_station_root":target,"continuity_verified":True}
