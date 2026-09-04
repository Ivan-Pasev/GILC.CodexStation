from dataclasses import dataclass,asdict
from .authority import authorize
from .integrity import sha256_obj
@dataclass(frozen=True)
class EffectReceipt:
    intent_digest:str;prestate_digest:str;poststate_digest:str;authority:str;witness:str;executed:bool
def execute_simulated(intent,granted,prestate,poststate,witness):
    authorize(intent,granted)
    if not witness.strip(): raise ValueError("witness required")
    return EffectReceipt(sha256_obj(asdict(intent)),sha256_obj(prestate),sha256_obj(poststate),granted.name,witness,True)
