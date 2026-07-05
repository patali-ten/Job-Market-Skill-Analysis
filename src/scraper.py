import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
API_URL = "https://remoteok.com/api"

def fetch_jobs(tag=""):
    """
    Fetch job listings from RemoteOK's public JSON API.
    tag: optional category filter, e.g. 'python', 'data', 'marketing'
    """
    url = f"{API_URL}?tags={tag}" if tag else API_URL
    response = requests.get(url, headers=HEADERS, timeout=10)
    
    if response.status_code != 200:
        print(f"Failed to fetch tag='{tag}': status {response.status_code}")
        return []
    
    data = response.json()
    # RemoteOK's first item is always a "legal notice" object, not a job — skip it
    jobs = [item for item in data if "id" in item]
    return jobs


def clean_description(raw_html):
    """
    RemoteOK descriptions are stored as HTML. Use BeautifulSoup
    to strip tags and return clean, readable plain text.
    """
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text


def scrape_multiple_categories(tags, delay=2):
    """
    Loop through a fixed list of job-category tags,
    fetch each, clean descriptions, and combine into one list.
    """
    all_jobs = []
    
    for tag in tags:
        print(f"Fetching jobs for tag: {tag}")
        jobs = fetch_jobs(tag)
        
        for job in jobs:
            all_jobs.append({
                "title": job.get("position", ""),
                "company": job.get("company", ""),
                "location": job.get("location", "Worldwide/Remote"),
                "tags": ", ".join(job.get("tags", [])),
                "description": clean_description(job.get("description", "")),
                "apply_url": job.get("url", ""),
                "date_posted": job.get("date", ""),
                "search_tag": tag
            })
        
        time.sleep(delay)  # ethical delay between requests
    
    return all_jobs


if __name__ == "__main__":
    # Mix of data-focused and broader tech/non-tech tags —
    # since this is a general job-market analysis, not just data roles
    job_tags = ["data", "python", "sql", "marketing", "design", "product"]
    
    results = scrape_multiple_categories(job_tags, delay=2)
    
    df = pd.DataFrame(results)
    df.drop_duplicates(subset=["title", "company", "apply_url"], inplace=True)
    
    print(f"\nTotal unique jobs collected: {len(df)}")
    print(df[["title", "company", "location"]].head(3))

    # --- SMART DYNAMIC PATHS ---
    # 1. Get the absolute path of the directory containing scraper.py (which is src/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Go up one level to the project root directory
    root_dir = os.path.dirname(script_dir)
    
    # 3. Target the main data folder at the root level
    target_data_dir = os.path.join(root_dir, "data")
    
    # 4. Ensure the root data folder exists (just in case)
    os.makedirs(target_data_dir, exist_ok=True)
    
    # 5. Define the final save path
    save_path = os.path.join(target_data_dir, "raw_data.csv")
    # ----------------------------
    
    df.to_csv(save_path, index=False)
    print(f"Saved to {save_path}")