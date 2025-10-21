import re

def filter_jobs(jobs, include_keywords, exclude_keywords):
    """Filter jobs by include/exclude keywords (case-insensitive)."""
    results = []
    for job in jobs:
        title = job["title"]
        title_lower = title.lower()

        include_match = any(re.search(rf"\b{re.escape(k.lower())}\b", title_lower)
                            for k in include_keywords)
        exclude_match = any(re.search(rf"\b{re.escape(k.lower())}\b", title_lower)
                            for k in exclude_keywords)

        if include_match and not exclude_match:
            results.append(job)
    return results