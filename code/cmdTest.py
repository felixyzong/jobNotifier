import json
from pathlib import Path
from jobFetchAlgolia import fetch_algolia_jobs
from jobFetchJson import fetch_script_json_jobs
from jobFilter import filter_jobs

CONFIG_FILE = Path("config.json")


def save_config(data):
    """Write updated config.json to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    if not CONFIG_FILE.exists():
        print("config.json not found.")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    for site in config["websites"]:
        print(f"\nChecking: {site['name']}")

        # Skip sites that failed previously
        if site.get("failedLastTime", False):
            print(f"Skipped (failedLastTime=True). Fix manually to retry.")
            continue

        # Choose the fetching method
        if site["type"] == "algolia":
            jobs = fetch_algolia_jobs(site)
        elif site["type"] == "script_json":
            jobs = fetch_script_json_jobs(site)
        else:
            print(f"Unsupported site type: {site['type']}")
            continue

        if not jobs:
            if not site.get("failedLastTime", False):
                print(f"No jobs fetched from {site['name']}")
            continue

        # Reset failed flag if successful
        site["failedLastTime"] = False

        # Apply keyword filters
        filtered = filter_jobs(
            jobs,
            site.get("include_keywords", []),
            site.get("exclude_keywords", [])
        )

        if filtered:
            print(f"{len(filtered)} job(s) match filters on {site['name']}:")
            for job in filtered:
                print(f"- {job['title']}\n  {job['url']}")
        else:
            print("No matching jobs after filtering.")

    # Save updated config with failedLastTime states
    save_config(config)
    print("\nConfig updated.")


if __name__ == "__main__":
    main()