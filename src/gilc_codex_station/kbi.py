from dataclasses import dataclass
from typing import Callable,Any
@dataclass(frozen=True)
class Invariant: invariant_id:str;predicate:Callable[[Any],bool];description:str
@dataclass(frozen=True)
class InvariantResult: invariant_id:str;passed:bool;description:str
def evaluate(c,inv): return [InvariantResult(i.invariant_id,bool(i.predicate(c)),i.description) for i in inv]
def require_all(rs):
    f=[r.invariant_id for r in rs if not r.passed]
    if f: raise ValueError("KBI invariant failure:"+",".join(f))
