
import os
import json
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ENV_FILE = BASE_DIR / ".env"
OUTPUT_FILE = DATA_DIR / "competitions_raw.json"

# Create data directory
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load your single Master API Key
if not ENV_FILE.is_file():
    sys.exit(f"ERROR: .env file not found: {ENV_FILE}")

load_dotenv(ENV_FILE, override=True)

api_key = os.getenv("SPORTRADAR_API_KEY", "").strip()

if not api_key:
    sys.exit(
        "ERROR: Master API Key is missing. "
        "Add SPORTRADAR_API_KEY to your .env file."
    )

# SportRadar Tennis Competitions endpoint.
# This access level must match your SportRadar subscription.
API_URL = (
    "https://api.sportradar.com/tennis/trial/v3/en/"
    "competitions.json"
)

HEADERS = {
    "x-api-key": api_key,
    "Accept": "application/json",
}


def fetch_competitions():
    print("Connecting to SportRadar Tennis Competitions API...")

    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=30,
        )

        if response.status_code != 200:
            print(f"Request failed: HTTP {response.status_code}")

            if response.status_code == 401:
                print("Authentication failed. Verify your Master API Key.")
            elif response.status_code == 403:
                print(
                    "Access denied. Verify Tennis API permissions and "
                    "whether your account uses Trial or Production access."
                )
            elif response.status_code == 429:
                print("Rate limit reached. Please wait before retrying.")
            else:
                print("Response:", response.text[:500])

            return

        try:
            data = response.json()
        except ValueError:
            print("ERROR: The API did not return valid JSON.")
            return

        competitions = data.get("competitions")

        if not isinstance(competitions, list):
            print("ERROR: No competitions list was found in the response.")
            print("Response fields:", list(data.keys()))
            return

        # Save the raw response
        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

        print("\nSUCCESS: Competitions downloaded.")
        print("Total competitions:", len(competitions))
        print("Saved to:", OUTPUT_FILE)

        if competitions:
            print("\nFirst competition sample:")
            print(
                json.dumps(
                    competitions[0],
                    indent=2,
                    ensure_ascii=False,
                )
            )

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect. Check your internet connection.")
    except requests.exceptions.RequestException as error:
        print("ERROR: Request failed:", error)
    except OSError as error:
        print("ERROR: Could not save the JSON file:", error)


if __name__ == "__main__":
    fetch_competitions()
