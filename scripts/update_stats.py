import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path

from playwright.sync_api import sync_playwright

# ==========================================================
# CONFIG
# ==========================================================

USER_ID = 638152
USERNAME = "itsskipped"

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

USER_DATA = r"C:\Users\sukep\AppData\Local\BraveSoftware\Brave-Browser\User Data"

PROFILE = "Default"

API = f"/api/users/{USER_ID}/gym_stats/"

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT = DATA_DIR / "stats.json"

# ==========================================================
# MAIN
# ==========================================================

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        executable_path=BRAVE_PATH,
        user_data_dir=USER_DATA,
        headless=False,
        args=[
            f"--profile-directory={PROFILE}"
        ]
    )

    try:

        # gunakan tab yang sudah ada jika ada
        if context.pages:
            page = context.pages[0]
        else:
            page = context.new_page()

        print("[+] Opening CyLab...")

        page.goto(
            "https://learn.cylabacademy.org/dashboard",
            wait_until="networkidle"
        )

        print("[+] Fetching API...")

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

        overall = api["overall"]

        stats = {

            "username": USERNAME,

            "updated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),

            "overall": {

                "available": overall["available"],

                "solved": overall["solved"],

                "retired": overall["retired_solved"],

                "percentage": round(
                    overall["solved"] /
                    overall["available"] * 100,
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
                    d["solved"] /
                    d["available"] * 100,
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

        # ==========================================================
        # SAVE JSON
        # ==========================================================

        with OUTPUT.open("w", encoding="utf-8") as f:
            json.dump(stats, f, indent=4)

        print(f"[+] Saved -> {OUTPUT}")

        # ==========================================================
        # GIT
        # ==========================================================

        status = subprocess.run(
            ["git", "status", "--porcelain", "data/stats.json"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        if status.stdout.strip():

            print("[+] Git changes detected")

            subprocess.run(
                ["git", "add", "data/stats.json"],
                cwd=BASE_DIR,
                check=True
            )

            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"Update CyLab stats ({stats['overall']['solved']} solves)"
                ],
                cwd=BASE_DIR,
                check=True
            )

            subprocess.run(
                ["git", "push"],
                cwd=BASE_DIR,
                check=True
            )

            print("[+] Git push completed")

        else:

            print("[+] No changes detected")

    finally:

        context.close()