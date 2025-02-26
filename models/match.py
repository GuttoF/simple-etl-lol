from typing import List

from pydantic import BaseModel


class MatchPlayer(BaseModel):
    kills: int
    deaths: int
    assists: int
    item0: int
    item1: int
    item2: int
    item3: int
    item4: int
    item5: int
    totalMinionsKilled: int
    goldEarned: int
    puuid: str
    win: bool
    championId: int


class MatchInfo(BaseModel):
    gameCreation: int
    gameDuration: int
    gameMode: str
    participants: List[MatchPlayer]


class Match(BaseModel):
    matchId: str
    info: MatchInfo
