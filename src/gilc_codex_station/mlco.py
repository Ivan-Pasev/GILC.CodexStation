from dataclasses import dataclass
from enum import Enum
from .integrity import sha256_obj
class Role(str,Enum):
    PERCEPTOR="PERCEPTOR";RETRIEVER="RETRIEVER";THEORIST="THEORIST";FORMALIZER="FORMALIZER";ARCHITECT="ARCHITECT";ADVERSARY="ADVERSARY";VERIFIER="VERIFIER";PLANNER="PLANNER";ORCHESTRATOR="ORCHESTRATOR";WITNESS="WITNESS"
@dataclass(frozen=True)
class RoleResult: role:Role;task_id:str;output:str;lineage_id:str
@dataclass(frozen=True)
class ReconciliationWitness: task_id:str;lineage_id:str;roles:tuple[str,...];digest:str
def reconcile(rs):
    if not rs: raise ValueError("no role results")
    if len({r.task_id for r in rs})!=1 or len({r.lineage_id for r in rs})!=1: raise ValueError("cross-task or cross-lineage reconciliation denied")
    p=[{"role":r.role.value,"output":r.output} for r in sorted(rs,key=lambda x:x.role.value)]
    return ReconciliationWitness(rs[0].task_id,rs[0].lineage_id,tuple(x["role"] for x in p),sha256_obj(p))
