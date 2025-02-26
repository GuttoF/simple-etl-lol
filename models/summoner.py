from pydantic import BaseModel


class SummonerProfile(BaseModel):
    id: str
    accountId: str
    puuid: str
    name: str
    profileIconId: int
    revisionDate: int
    summonerLevel: int


class SummonerIds(BaseModel):
    puuid: str
    gameName: str
    tagLine: str
