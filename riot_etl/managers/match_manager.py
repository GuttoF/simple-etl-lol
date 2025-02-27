from datetime import datetime
from typing import Any, Dict, List

from config.settings import BASE_REGIONS
from riot_etl.managers.db_manager import DatabaseManager
from riot_etl.managers.riot_request_manager import RiotRequestManager
from riot_etl.models.match import Match


class MatchManager:
    def __init__(self, riot_manager: RiotRequestManager):
        self.riot_manager = riot_manager

    async def get_ranked_matches(
        self, puuid: str, region: str, count: int = 20
    ) -> List[str]:
        try:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {"queue": 420, "start": 0, "count": count}
            response = await self.riot_manager.get_request(url, params)
            return response
        except Exception as e:
            raise Exception(f"Failed to get match list: {str(e)}")

    async def get_match_details(self, match_id: str, region: str) -> Match:
        try:
            url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match_data = await self.riot_manager.get_request(url)
            return Match(**match_data)
        except Exception as e:
            raise Exception(f"Failed to get match details for {match_id}: {str(e)}")

    def process_match_data(
        self, match: Match, puuid: str, player_name: str, region: str
    ) -> Dict[str, Any]:
        try:
            player = next(p for p in match.info.participants if p["puuid"] == puuid)

            # Debug prints
            print(f"Player Name: {player_name}")
            print(f"Region: {region}")

            return {
                "match_id": match.metadata.matchId,
                "puuid": puuid,
                "player_name": player_name,
                "region": region,
                "timestamp": datetime.fromtimestamp(match.info.gameCreation / 1000),
                "duration": match.info.gameDuration,
                "game_mode": match.info.gameMode,
                "win": player["win"],
                "kills": player["kills"],
                "deaths": player["deaths"],
                "assists": player["assists"],
                "cs": player["totalMinionsKilled"],
                "gold": player["goldEarned"],
                "items": [
                    player["item0"],
                    player["item1"],
                    player["item2"],
                    player["item3"],
                    player["item4"],
                    player["item5"],
                ],
            }

        except Exception as e:
            raise Exception(f"Failed to process match data: {str(e)}")


async def fetch_and_save_matches(summoner_name: str, region_code: str = "br1") -> None:
    riot_manager = RiotRequestManager()
    match_manager = MatchManager(riot_manager)
    db_manager = DatabaseManager()

    try:
        print(f"Fetching data for {summoner_name}...")

        summoner = await riot_manager.get_summoner_by_name(
            summoner_name, BASE_REGIONS[region_code], region_code
        )

        print(f"Found summoner: {summoner.name} (Level {summoner.summonerLevel})")

        db_manager.save_summoner(summoner.model_dump())

        print("Fetching ranked matches...")
        match_ids = await match_manager.get_ranked_matches(
            summoner.puuid, BASE_REGIONS[region_code]
        )

        if not match_ids:
            print("No ranked matches found.")
            return

        print(f"Found {len(match_ids)} matches. Processing...")

        matches_data: list[dict[str, Any]] = []
        for i, match_id in enumerate(match_ids, 1):
            print(f"Processing match {i}/{len(match_ids)}: {match_id}")
            try:
                match = await match_manager.get_match_details(
                    match_id, BASE_REGIONS[region_code]
                )
                processed_data: dict[str, Any] = match_manager.process_match_data(
                    match, summoner.puuid, summoner_name, region_code
                )
                matches_data.append(processed_data)

            except Exception as e:
                print(f"Error processing match {match_id}: {str(e)}")
                continue

        if matches_data:
            db_manager.save_matches(matches_data)
            print(f"Saved {len(matches_data)} matches to database")

        while True:
            print("\nAvailable options:")
            print("1. View matches as DataFrame")
            print("2. Export matches to CSV")
            print("3. Exit")

            choice = input("\nChoose an option (1-3): ")

            match choice:
                case "1":
                    df = db_manager.get_summoner_matches_df(summoner.puuid)
                    print("\nMatches DataFrame:")
                    print(df)
                case "2":
                    filepath = db_manager.export_to_csv(summoner.puuid)
                    print(f"\nData exported to: {filepath}")
                case "3":
                    break
                case _:
                    print("Invalid option!")

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db_manager.close()
