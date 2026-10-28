"""Fetch tennis complexes (with nested venues) from the SportRadar API.

Saves the untouched API response to data/complexes_venues_raw.json.
Run this first, then process_complexes_venues.py.
"""

import json
import sys
import time
from pathlib import Path

import requests

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ENV_FILE = BASE_DIR / ".env"
OUTPUT_FILE = DATA_DIR / "complexes_venues_raw.json"

# Create data directory
DATA_DIR.mkdir(parents=True, exist_ok=True)



def read_api_key(env_path):
    """Read SPORTRADAR_API_KEY from a .env file.

    Handles common Windows problems: a UTF-8 BOM, UTF-16 files created with
    PowerShell, and quotes or spaces around the value.
    Returns the key and the list of variable names found (never the values).
    """
    raw = env_path.read_bytes()

    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig", errors="replace")

    found_names = []
    key_value = ""

    for line in text.splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        name = name.replace("export ", "").strip()
        found_names.append(name)

        if name == "SPORTRADAR_API_KEY":
            key_value = value.strip().strip('"').strip("'").strip()

    return key_value, found_names


# Load the API key from the local .env file (never commit this file)
if not ENV_FILE.is_file():
    similar = sorted(
        item.name for item in BASE_DIR.iterdir() if item.name.startswith(".env")
    )
    sys.exit(
        f"ERROR: .env file not found in {BASE_DIR}\n"
        f"Files starting with .env in this folder: {similar or 'none'}\n"
        "The file must be named exactly .env (not .env.txt) and sit next to "
        "this script."
    )

api_key, env_names = read_api_key(ENV_FILE)

if not api_key:
    sys.exit(
        "ERROR: SPORTRADAR_API_KEY is missing or empty in your .env file.\n"
        f"Variable names found in the file: {env_names or 'none'}\n"
        "The line must look like: SPORTRADAR_API_KEY=your_key"
    )

if api_key == "PASTE_YOUR_API_KEY_HERE":
    sys.exit(
        "ERROR: .env still contains the placeholder. "
        "Replace PASTE_YOUR_API_KEY_HERE with your real key."
    )

# SportRadar Tennis Complexes endpoint.
# The access level (trial/production) must match your subscription.
API_URL = (
    "https://api.sportradar.com/tennis/trial/v3/en/"
    "complexes.json"
)

HEADERS = {
    "x-api-key": api_key,
    "Accept": "application/json",
}

MAX_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 5


def fetch_complexes_venues():
    """Download the complexes response and save it as raw JSON."""
    print("Connecting to SportRadar Tennis Complexes API...")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                API_URL,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 429:
                # Rate limit: wait longer each time, then retry.
                wait = RETRY_WAIT_SECONDS * attempt
                print(
                    f"Rate limit reached (attempt {attempt}/{MAX_ATTEMPTS}). "
                    f"Waiting {wait} seconds..."
                )
                time.sleep(wait)
                continue

            if response.status_code != 200:
                print(f"Request failed: HTTP {response.status_code}")

                if response.status_code == 401:
                    print("Authentication failed. Verify your API key.")
                elif response.status_code == 403:
                    print(
                        "Access denied. Verify Tennis API permissions and "
                        "whether your account uses Trial or Production access."
                    )
                else:
                    print("Response:", response.text[:500])

                return

            try:
                data = response.json()
            except ValueError:
                print("ERROR: The API did not return valid JSON.")
                return

            complexes = data.get("complexes")

            if not isinstance(complexes, list):
                print("ERROR: No complexes list was found in the response.")
                print("Response fields:", list(data.keys()))
                return

            # Save the raw response
            with OUTPUT_FILE.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            venue_total = sum(
                len(item.get("venues") or [])
                for item in complexes
                if isinstance(item, dict)
            )

            print("\nSUCCESS: Complexes downloaded.")
            print("Total complexes:", len(complexes))
            print("Total nested venues:", venue_total)
            print("Saved to:", OUTPUT_FILE)

            if complexes:
                print("\nFirst complex sample:")
                print(
                    json.dumps(
                        complexes[0],
                        indent=2,
                        ensure_ascii=False,
                    )
                )

            return

        except requests.exceptions.Timeout:
            print("ERROR: Request timed out.")
            return
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect. Check your internet connection.")
            return
        except requests.exceptions.RequestException as error:
            print("ERROR: Request failed:", error)
            return
        except OSError as error:
            print("ERROR: Could not save the JSON file:", error)
            return

    print("ERROR: Rate limit still active after all retries. Try again later.")


if __name__ == "__main__":
    fetch_complexes_venues()
