import asyncio
import sys

from config.settings import BASE_REGIONS
from riot_etl.managers.match_manager import fetch_and_save_matches
from riot_etl.scraper.scraper import LeagueScraper

URLS = [
    "https://www.leagueofgraphs.com/pt/rankings/summoners/br",
    "https://www.leagueofgraphs.com/pt/rankings/summoners/br?page=2",
]


def main() -> None:
    scraper = LeagueScraper()
    players = scraper.load_tags(URLS)

    print(f"Found {len(players)} players in challanger:")

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
