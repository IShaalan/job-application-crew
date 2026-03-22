#!/usr/bin/env python3
"""
Interactive setup script for Google Drive export.

Walks users through:
1. Creating a Google Cloud project and enabling APIs
2. Setting up OAuth credentials
3. Running the OAuth flow to generate tokens
4. Configuring the output folder

Usage:
    python scripts/setup_google_drive.py
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
DRIVE_CONFIG_PATH = os.path.join(CONFIG_DIR, "drive_config.yaml")

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_header(text: str) -> None:
    print(f"\n{text}")
    print("=" * len(text))


def print_step(number: int, title: str, body: str) -> None:
    print(f"\nStep {number}: {title}")
    print("-" * (8 + len(title)))
    for line in body.strip().splitlines():
        print(f"  {line}")
    print()


def ensure_config_dir() -> None:
    """Create the config/ directory if it doesn't exist."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def check_dependencies() -> bool:
    """Verify required libraries are installed. Return True if all present."""
    missing = []

    try:
        import google.auth  # noqa: F401
    except ImportError:
        missing.append("google-auth")

    try:
        import google_auth_oauthlib  # noqa: F401
    except ImportError:
        missing.append("google-auth-oauthlib")

    try:
        import yaml  # noqa: F401
    except ImportError:
        missing.append("pyyaml")

    if missing:
        print_header("Missing Dependencies")
        print("\nThe following Python packages are required but not installed:\n")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall them with:\n")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all export dependencies at once:\n")
        print("  pip install google-auth google-auth-oauthlib google-api-python-client pyyaml")
        print()
        return False

    return True


def show_setup_instructions() -> None:
    """Print step-by-step instructions for creating GCP credentials."""
    print_header("Google Drive Export Setup")

    print_step(
        1,
        "Create a Google Cloud Project",
        """\
1. Go to https://console.cloud.google.com
2. Create a new project (or select an existing one)
3. Enable the Google Docs API and Google Drive API
   - Go to APIs & Services > Library
   - Search for "Google Docs API" and click Enable
   - Search for "Google Drive API" and click Enable""",
    )

    print_step(
        2,
        "Create OAuth Credentials",
        """\
1. Go to APIs & Services > Credentials
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User type: External (or Internal if using Workspace)
   - Fill in the required fields, then return to Credentials
4. Application type: "Desktop app"
5. Download the JSON file
6. Save it as: config/credentials.json""",
    )

    print_step(
        3,
        "Create an output folder in Google Drive",
        """\
1. Open Google Drive (https://drive.google.com)
2. Create a folder where exported resumes will be saved
3. Open the folder and copy the folder ID from the URL
   (It's the long string after /folders/ in the URL)
   Example: https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ
                                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                    This part is the folder ID""",
    )


def wait_for_credentials() -> bool:
    """Wait for the user to place credentials.json, then verify it exists."""
    input("Press Enter when you've completed the steps above...")
    print()

    if not os.path.isfile(CREDENTIALS_PATH):
        print(f"credentials.json not found at: {CREDENTIALS_PATH}")
        print()
        retry = input("Would you like to try again? (y/n): ").strip().lower()
        if retry in ("y", "yes"):
            print()
            input("Place credentials.json in config/ and press Enter...")
            print()

    if not os.path.isfile(CREDENTIALS_PATH):
        print("Error: credentials.json still not found.")
        print(f"Expected location: {CREDENTIALS_PATH}")
        print("\nPlease download the OAuth credentials JSON from Google Cloud Console")
        print("and save it to the path shown above, then re-run this script.")
        return False

    # Quick sanity check: is it valid JSON?
    try:
        with open(CREDENTIALS_PATH, "r") as f:
            data = json.load(f)
        if "installed" not in data and "web" not in data:
            print("Warning: credentials.json does not look like a standard OAuth client file.")
            print("Expected a JSON object with an 'installed' or 'web' key.")
            print("Make sure you downloaded the correct file from Google Cloud Console.\n")
            proceed = input("Continue anyway? (y/n): ").strip().lower()
            if proceed not in ("y", "yes"):
                return False
    except json.JSONDecodeError:
        print("Error: credentials.json is not valid JSON.")
        print("Please re-download the file from Google Cloud Console.")
        return False

    print("credentials.json found and validated.")
    return True


def ask_folder_id() -> str:
    """Prompt the user for their Google Drive output folder ID."""
    print()
    print("Enter your Google Drive output folder ID.")
    print("(The long string from the folder URL, e.g. 1aBcDeFgHiJkLmNoPqRsTuVwXyZ)")
    print()

    while True:
        folder_id = input("Folder ID: ").strip()
        if folder_id:
            return folder_id
        print("Folder ID cannot be empty. Please try again.\n")


def run_oauth_flow() -> bool:
    """Run the OAuth2 flow and save tokens."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: google-auth-oauthlib is not installed.")
        print("Run: pip install google-auth-oauthlib")
        return False

    print("\nStarting OAuth authorization flow...")
    print("A browser window will open for you to authorize access.\n")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    except Exception as e:
        print(f"\nOAuth flow failed: {e}\n")
        print("Troubleshooting:")
        print("  1. Make sure credentials.json is a valid OAuth Desktop client file")
        print("  2. Check that Google Docs API and Google Drive API are enabled")
        print("  3. If using a firewall/proxy, ensure localhost is accessible")
        print("  4. Try running the script again; sometimes the browser handoff is slow")
        print("  5. Make sure you selected 'Desktop app' as the application type")
        print("     (not 'Web application')")
        return False

    # Save the token
    ensure_config_dir()
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())

    print(f"Authorization successful. Token saved to: {TOKEN_PATH}")
    return True


def save_drive_config(folder_id: str) -> None:
    """Write the drive_config.yaml file."""
    import yaml

    ensure_config_dir()
    config = {"output_folder_id": folder_id}

    with open(DRIVE_CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Drive config saved to: {DRIVE_CONFIG_PATH}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print_header("Job Application Crew - Google Drive Setup")
    print("\nThis script will configure Google Drive export for your resumes")
    print("and cover letters.\n")

    # 0. Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # 1. Check if credentials already exist
    ensure_config_dir()
    credentials_exist = os.path.isfile(CREDENTIALS_PATH)

    if credentials_exist:
        print(f"Found existing credentials at: {CREDENTIALS_PATH}")
        reuse = input("Use existing credentials? (y/n): ").strip().lower()
        if reuse not in ("y", "yes"):
            credentials_exist = False

    # 2. Show instructions if credentials are not present
    if not credentials_exist:
        show_setup_instructions()
        if not wait_for_credentials():
            sys.exit(1)

    # 3. Check if token already exists
    token_exists = os.path.isfile(TOKEN_PATH)
    run_auth = True

    if token_exists:
        print(f"\nFound existing token at: {TOKEN_PATH}")
        reauth = input("Re-authorize? (y/n): ").strip().lower()
        if reauth not in ("y", "yes"):
            run_auth = False
            print("Keeping existing authorization.")

    # 4. Run OAuth flow
    if run_auth:
        if not run_oauth_flow():
            sys.exit(1)

    # 5. Ask for folder ID
    config_exists = os.path.isfile(DRIVE_CONFIG_PATH)
    existing_folder_id = None

    if config_exists:
        try:
            import yaml

            with open(DRIVE_CONFIG_PATH, "r") as f:
                existing_config = yaml.safe_load(f)
            existing_folder_id = existing_config.get("output_folder_id")
        except Exception:
            pass

    if existing_folder_id:
        print(f"\nExisting output folder ID: {existing_folder_id}")
        change = input("Change it? (y/n): ").strip().lower()
        if change in ("y", "yes"):
            folder_id = ask_folder_id()
        else:
            folder_id = existing_folder_id
            print("Keeping existing folder ID.")
    else:
        folder_id = ask_folder_id()

    # 6. Save config
    save_drive_config(folder_id)

    # 7. Done
    print()
    print_header("Setup Complete")
    print()
    print("Google Drive export is now configured.")
    print("Use: /job-application export --format gdrive")
    print()
    print("Files created:")
    if os.path.isfile(TOKEN_PATH):
        print(f"  - {TOKEN_PATH}")
    print(f"  - {DRIVE_CONFIG_PATH}")
    print()
    print("Note: config/ is in .gitignore -- your credentials won't be committed.")
    print()


if __name__ == "__main__":
    main()
