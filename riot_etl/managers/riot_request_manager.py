import asyncio
from typing import Any, Dict, Optional

import httpx

from config.settings import RIOT_API_KEY
from riot_etl.models.summoner import SummonerIds, SummonerProfile

if RIOT_API_KEY is None:
    raise ValueError("RIOT_API_KEY must be set in the configuration.")
from riot_etl.managers.rate_limit_manager import RateLimitManager


class RiotRequestManager:
    def __init__(self) -> None:
        self.api_key = RIOT_API_KEY
        self.rate_limiter = RateLimitManager()
        self.headers: Dict[str, str] = {
            "X-Riot-Token": self.api_key,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",  # noqa
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "Content-Type": "application/json",
        }

    async def get_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        await self.rate_limiter.wait_if_needed()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    print(f"Response data type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Response data keys: {data.keys()}")
                    elif isinstance(data, list):
                        print(f"Response data length: {len(data)}")
                    else:
                        print(f"Response data: {data}")
                    return data
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    return await self.get_request(url, params)
                else:
                    raise Exception(f"API Error: {response.status_code} - {response.text}")

            except httpx.RequestError as e:
                raise Exception(f"Request failed: {str(e)}")


    async def get_summoner_by_name(self, summoner_name: str, region: str, server_code: str) -> SummonerProfile:
        try:
            account_tagline = summoner_name.replace("#", "/")
            
            url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{account_tagline}"
            account_data = await self.get_request(url)
            print(f"Account data: {account_data}")  # Debug print
            account_id = SummonerIds(**account_data)
    
            url = f"https://{server_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{account_id.puuid}"
            summoner_data = await self.get_request(url)
            print(f"Summoner data: {summoner_data}")  # Debug print
            
            # Adicione o nome do account_id aos dados do invocador
            summoner_data['name'] = account_id.gameName
            
            summoner = SummonerProfile(**summoner_data)
            return summoner
            
        except Exception as e:
            raise Exception(f"Failed to get summoner data: {str(e)}")

