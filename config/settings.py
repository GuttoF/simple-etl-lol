import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# LTA north and south
BASE_REGIONS = {
    "br1": "americas",
    "na1": "americas",
    "la1": "americas",
    "la2": "americas",
}
