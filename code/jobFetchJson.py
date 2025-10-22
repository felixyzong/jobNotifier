import requests
import html
import json
from bs4 import BeautifulSoup

def fetch_script_json_jobs(site):
    """Fetch jobs embedded as JSON inside <script> tag (e.g., Behaviour Interactive)."""
    try:
        resp = requests.get(site["url"], timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Locate the <script> that contains display_jobboard(...)
        script_tag = next((s for s in soup.find_all("script") if "display_jobboard" in s.text), None)
        if not script_tag:
            print(f"No jobboard script found for {site['name']}")
            site["failedLastTime"] = True
            return []

        text = html.unescape(script_tag.text)

        # Find where the JSON array starts
        start = text.find("[{")
        if start == -1:
            print(f"No JSON start found for {site['name']}")
            site["failedLastTime"] = True
            return []

        # Read until brackets balance
        depth = 0
        end = None
        for i, ch in enumerate(text[start:], start=start):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if not end:
            print(f"Could not find complete JSON array for {site['name']}")
            site["failedLastTime"] = True
            return []

        json_text = text[start:end]

        # Now safely parse it as JSON
        try:
            jobs_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"JSON parse error for {site['name']}: {e}")
            site["failedLastTime"] = True
            return []

        # Build job list
        base_url = site.get("base_url", "").rstrip("/")
        jobs = []
        for job in jobs_data:
            title = job.get("post_title", "")
            link = job.get("link", "")
            if link and not link.startswith("http") and base_url:
                link = base_url + link
            jobs.append({"title": title, "url": link})

        return jobs

    except Exception as e:
        print(f"Fetch failed for {site['name']}: {e}")
        site["failedLastTime"] = True
        return []