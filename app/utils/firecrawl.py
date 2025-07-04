import requests
import os
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def crawl_url(url: str) -> dict:
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "url": url,
        "include_raw_html": False,
        "use_firecrawl_ai": True
    }

    try:
        response = requests.post("https://api.firecrawl.dev/v1/crawl", json=body, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get("success", False):
            return data
        else:
            # Handle unsupported domains, rate limits, etc.
            print(f"Firecrawl error for {url}: {data}")
            return {
                "url": url,
                "firecrawl_ai_summary": "Crawl failed or unsupported domain",
                "success": False
            }
    except Exception as e:
        print(f"Firecrawl exception for {url}: {str(e)}")
        return {
            "url": url,
            "firecrawl_ai_summary": "Crawl error occurred",
            "success": False
        }
