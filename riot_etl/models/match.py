from pydantic import BaseModel
from typing import List, Dict, Any

class MatchMetadata(BaseModel):
    matchId: str

class MatchInfo(BaseModel):
    gameCreation: int
    gameDuration: int
    gameMode: str
    participants: List[Dict[str, Any]]

class Match(BaseModel):
    metadata: MatchMetadata
    info: MatchInfo

    @property
    def matchId(self) -> str:
        return self.metadata.matchId

