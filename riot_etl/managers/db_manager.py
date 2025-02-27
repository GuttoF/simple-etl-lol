from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import duckdb
import pandas as pd


class DatabaseManager:
    def __init__(self, db_path: str = "riot_data.db") -> None:
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)  # type: ignore
        self._create_tables()

    def _create_tables(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS summoners (
                puuid VARCHAR PRIMARY KEY,
                summoner_id VARCHAR,
                account_id VARCHAR,
                name VARCHAR,
                profile_icon_id INTEGER,
                summoner_level INTEGER,
                last_updated TIMESTAMP
            )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id VARCHAR,
            puuid VARCHAR,
            player_name VARCHAR,
            region VARCHAR,
            timestamp TIMESTAMP,
            duration INTEGER,
            game_mode VARCHAR,
            win BOOLEAN,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            cs INTEGER,
            gold INTEGER,
            items VARCHAR,
            PRIMARY KEY (match_id, puuid)
            )
        """)

    def save_summoner(self, summoner_data: Dict[str, str | int]) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO summoners
            (puuid, summoner_id, account_id, name, profile_icon_id, summoner_level, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,  # noqa: E501
            (  # noqa: E501
                summoner_data["puuid"],
                summoner_data["id"],
                summoner_data["accountId"],
                summoner_data["name"],
                summoner_data["profileIconId"],
                summoner_data["summonerLevel"],
                datetime.now(),
            ),
        )

    def save_matches(self, matches_data: List[Dict[str, str | int | bool]]) -> None:
        for match in matches_data:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO matches
                (match_id, puuid, player_name, region, timestamp, duration, game_mode, win,
                kills, deaths, assists, cs, gold, items)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,  # noqa: E501
                (
                    match["match_id"],
                    match["puuid"],
                    match["player_name"],
                    match["region"],
                    match["timestamp"],
                    match["duration"],
                    match["game_mode"],
                    match["win"],
                    match["kills"],
                    match["deaths"],
                    match["assists"],
                    match["cs"],
                    match["gold"],
                    str(match["items"]),
                ),
            )

    def get_summoner_matches_df(self, puuid: str) -> pd.DataFrame:
        return self.conn.execute(
            """
            SELECT * FROM matches
            WHERE puuid = ?
            ORDER BY timestamp DESC
        """,
            [puuid],
        ).df()

    def get_all_matches_df(self) -> pd.DataFrame:
        return self.conn.execute("SELECT * FROM matches ORDER BY timestamp DESC").df()

    def export_to_csv(
        self, puuid: Optional[str] = None, filepath: Optional[Path] = None
    ) -> str:
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = Path(f"matches_export_{timestamp}.csv")
        else:
            filepath = Path(filepath)

        if puuid:
            df = self.get_summoner_matches_df(puuid)
        else:
            df = self.get_all_matches_df()

        df.to_csv(filepath, index=False)
        return str(filepath)

    def close(self):
        self.conn.close()
