from typing import Any, List

import requests
from bs4 import BeautifulSoup


class LeagueScraper:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            )
        }

    def extract_players_tags(self, url: str) -> list[str]:
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            players = soup.select("table tr td span.name")
            return [player.text.strip() for player in players]
        else:
            print(f"Error accessing {url}: {response.status_code}")
            return []

    def load_tags(self, urls: list[str]) -> list[str]:
        players_list: List[Any] = []
        for url in urls:
            players_list.extend(self.extract_players_tags(url))
        return players_list
