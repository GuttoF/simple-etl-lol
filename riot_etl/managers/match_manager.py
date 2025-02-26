from typing import List, Dict
from datetime import datetime
from riot_etl.models.match import Match
from riot_etl.managers.riot_request_manager import RiotRequestManager

class MatchManager:
    def __init__(self, riot_manager: RiotRequestManager):
        self.riot_manager = riot_manager

    async def get_ranked_matches(self, puuid: str, region: str, count: int = 20) -> List[str]:
        try:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {
                'queue': 420,  # Ranked Solo/Duo
                'start': 0,
                'count': count
            }
            matches = await self.riot_manager.get_request(url, params)
            return matches
        except Exception as e:
            raise Exception(f"Failed to get match list: {str(e)}")

    async def get_match_details(self, match_id: str, region: str) -> Match:
        try:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_data = await self.riot_manager.get_request(url)
            return Match(**match_data)
        except Exception as e:
            raise Exception(f"Failed to get match details for {match_id}: {str(e)}")


    def process_match_data(self, match: Match, puuid: str) -> Dict:
        try:
            player = next(p for p in match.info.participants if p['puuid'] == puuid)

            return {
                'match_id': match.metadata.matchId,
                'puuid': puuid,
                'timestamp': datetime.fromtimestamp(match.info.gameCreation / 1000),
                'duration': match.info.gameDuration,
                'game_mode': match.info.gameMode,
                'win': player['win'],
                'kills': player['kills'],
                'deaths': player['deaths'],
                'assists': player['assists'],
                'cs': player['totalMinionsKilled'],
                'gold': player['goldEarned'],
                'items': [player['item0'], player['item1'], player['item2'], 
                          player['item3'], player['item4'], player['item5']]
            }
        except Exception as e:
            raise Exception(f"Failed to process match data: {str(e)}")

