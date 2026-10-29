"""Fetch the SportRadar doubles competitor rankings response.

The API key is read from the ignored .env file in the repository root. The
key is never printed, written to output, or included in exception messages.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
ENV_FILE = REPO_DIR / ".env"
OUTPUT_FILE = DATA_DIR / "doubles_rankings_raw.json"
API_URL = (
    "https://api.sportradar.com/tennis/trial/v3/en/"
    "double_competitors_rankings.json"
)
MAX_ATTEMPTS = 3


def main() -> int:
    """Fetch and save the raw response, returning a process exit code."""
    if not ENV_FILE.is_file():
        print(f"ERROR: .env file not found: {ENV_FILE}")
        return 1

    load_dotenv(ENV_FILE, override=True)
    api_key = os.getenv("SPORTRADAR_API_KEY", "").strip()
    if not api_key:
        print("ERROR: SPORTRADAR_API_KEY is missing or empty in .env.")
        return 1

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"x-api-key": api_key, "Accept": "application/json"}

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(API_URL, headers=headers, timeout=30)
        except requests.exceptions.Timeout:
            print("ERROR: Request timed out.")
            return 1
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to SportRadar.")
            return 1
        except requests.exceptions.RequestException as error:
            print(f"ERROR: Request failed ({type(error).__name__}).")
            return 1

        if response.status_code == 429 and attempt < MAX_ATTEMPTS:
            wait_seconds = attempt * 5
            print(
                f"Rate limit received (attempt {attempt}/{MAX_ATTEMPTS}); "
                f"retrying in {wait_seconds} seconds."
            )
            time.sleep(wait_seconds)
            continue

        if response.status_code != 200:
            print(f"ERROR: Rankings request failed with HTTP {response.status_code}.")
            if response.status_code == 401:
                print("Authentication failed; verify the local API configuration.")
            elif response.status_code == 403:
                print("Access denied; verify the subscription and trial endpoint.")
            elif response.status_code == 429:
                print("Rate limit remained active after retries.")
            else:
                print("The response body was not saved because the request failed.")
            return 1

        try:
            payload = response.json()
        except ValueError:
            print("ERROR: SportRadar returned invalid JSON.")
            return 1

        if not isinstance(payload, dict):
            print("ERROR: Expected a JSON object at the response root.")
            return 1

        if not isinstance(payload.get("rankings"), list):
            print(
                "ERROR: The response does not contain a rankings list. "
                f"Top-level fields: {sorted(payload)}"
            )
            return 1

        try:
            OUTPUT_FILE.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as error:
            print(f"ERROR: Could not save the raw response ({type(error).__name__}).")
            return 1

        print("SUCCESS: Doubles rankings downloaded.")
        print(f"HTTP status: {response.status_code}")
        print(f"Top-level fields: {sorted(payload)}")
        print(f"Ranking groups: {len(payload['rankings'])}")
        print(f"Saved raw response: {OUTPUT_FILE}")
        return 0

    print("ERROR: Request could not be completed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
