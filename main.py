import asyncio
import sys
from typing import Any

from config.settings import BASE_REGIONS
from riot_etl.managers.db_manager import DatabaseManager
from riot_etl.managers.match_manager import MatchManager
from riot_etl.managers.riot_request_manager import RiotRequestManager


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
                    match, summoner.puuid
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


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <summoner_name> [region_code]")
        print("Example: python main.py 'Player#TAG' br1")
        return

    summoner_name = sys.argv[1]
    region_code = sys.argv[2] if len(sys.argv) > 2 else "br1"

    if region_code not in BASE_REGIONS:
        print(
            f"Invalid region code. Valid options are: {', '.join(BASE_REGIONS.keys())}"
        )
        return

    asyncio.run(fetch_and_save_matches(summoner_name, region_code))


if __name__ == "__main__":
    main()
