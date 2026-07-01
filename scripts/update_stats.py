import json
from datetime import datetime, UTC
from pathlib import Path
from ftplib import FTP_TLS

from playwright.sync_api import sync_playwright

# ======================================================
# CYLAB CONFIG
# ======================================================

USER_ID = 638152
USERNAME = "itsskipped"

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
USER_DATA = r"C:\Users\sukep\AppData\Local\BraveSoftware\Brave-Browser\User Data"
PROFILE = "Profile 1"

API = f"/api/users/{USER_ID}/gym_stats/"

# ======================================================
# PROJECT PATH
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT = DATA_DIR / "stats.json"

DATA_DIR.mkdir(exist_ok=True)

# ======================================================
# FTPS CONFIG
# ======================================================

FTP_HOST = "tsaqiffawwaz.it.student.pens.ac.id"
FTP_USER = "tsaqiffawwaz@it.student.pens.ac.id"
FTP_PASS = "PASSWORD_KAMU"

REMOTE_DIR = "/data"

# ======================================================
# FETCH CYLAB
# ======================================================

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        executable_path=BRAVE_PATH,
        user_data_dir=USER_DATA,
        headless=True,
        args=[
            f"--profile-directory={PROFILE}"
        ]
    )

    try:

        page = context.new_page()

        page.goto(
            "https://learn.cylabacademy.org/dashboard",
            wait_until="networkidle"
        )

        result = page.evaluate(f"""
        async () => {{

            const response = await fetch("{API}");

            if (!response.ok){{
                return {{
                    ok:false,
                    status:response.status,
                    text:await response.text()
                }};
            }}

            return {{
                ok:true,
                data:await response.json()
            }};
        }}
        """)

        if not result["ok"]:
            raise Exception(result["text"])

        api = result["data"]

    finally:
        context.close()

# ======================================================
# BUILD JSON
# ======================================================

overall = api["overall"]

stats = {
    "username": USERNAME,
    "updated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    "overall": {
        "available": overall["available"],
        "solved": overall["solved"],
        "retired": overall["retired_solved"],
        "percentage": round(
            overall["solved"] / overall["available"] * 100,
            2
        )
    },
    "difficulty": {},
    "categories": {}
}

difficulty_map = {
    "1": "easy",
    "2": "medium",
    "3": "hard"
}

for key, name in difficulty_map.items():

    d = api["by_difficulty"][key]

    stats["difficulty"][name] = {
        "available": d["available"],
        "solved": d["solved"],
        "retired": d["retired_solved"],
        "percentage": round(
            d["solved"] / d["available"] * 100,
            2
        ) if d["available"] else 0
    }

for category, value in api["by_category"].items():

    stats["categories"][category] = {
        "available": value["overall"]["available"],
        "solved": value["overall"]["solved"],
        "retired": value["overall"]["retired_solved"],
        "percentage": round(
            value["overall"]["solved"] /
            value["overall"]["available"] * 100,
            2
        )
    }

# ======================================================
# SAVE LOCAL
# ======================================================

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(stats, f, indent=4)

print("Local JSON updated.")

# ======================================================
# UPLOAD FTPS
# ======================================================

print("Connecting FTPS...")

ftp = FTP_TLS(FTP_HOST)

ftp.login(FTP_USER, FTP_PASS)

ftp.prot_p()

ftp.cwd(REMOTE_DIR)

with open(OUTPUT, "rb") as f:
    ftp.storbinary("STOR stats.json", f)

ftp.quit()

print("Upload selesai!")