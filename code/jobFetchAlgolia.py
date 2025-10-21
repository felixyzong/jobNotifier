import requests

def fetch_algolia_jobs(site):
    headers = {
        "X-Algolia-Application-Id": site["algolia_app_id"],
        "X-Algolia-API-Key": site["algolia_api_key"],
        "Content-Type": "application/json",
    }

    index_name = site.get("index_name") or site.get("indexName")
    facet_filters = site.get("facet_filters", [])
    query = site.get("query", "")
    
    payload = {
        "requests": [
            {
                "indexName": index_name,
                "params": f"query={query}&hitsPerPage=100&page=0"
            }
        ]
    }

    # Algolia also accepts the structured filters field directly:
    payload["requests"][0]["facetFilters"] = facet_filters

    try:
        resp = requests.post(site["url"], headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        hits = data["results"][0]["hits"]

        base_url = site.get("base_url", "").rstrip("/")
        jobs = []
        for h in hits:
            title = h.get("title", "")
            link = h.get("link") or h.get("url") or ""
            if link and not link.startswith("http") and base_url:
                link = base_url + link
            jobs.append({"title": title, "url": link})
        return jobs

    except Exception as e:
        print(f"Fetch failed for {site['name']}: {e}")
        site["failedLastTime"] = True
        return []


