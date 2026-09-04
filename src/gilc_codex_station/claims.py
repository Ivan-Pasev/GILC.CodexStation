from dataclasses import dataclass
from enum import Enum
class ClaimDomain(str,Enum): SELF="SELF"; WORLD="WORLD"
class EpistemicStatus(str,Enum): OBSERVED="OBSERVED";HYPOTHESIS="HYPOTHESIS";VERIFIED="VERIFIED";UNKNOWN="UNKNOWN";CONFLICTED="CONFLICTED"
@dataclass(frozen=True)
class Claim:
    proposition:str;domain:ClaimDomain;status:EpistemicStatus;source:str|None=None;confidence:float|None=None
    def assert_world_truth(self): return self.domain is ClaimDomain.WORLD and self.status is EpistemicStatus.VERIFIED and bool(self.source)
