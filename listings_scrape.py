
import asyncio
from typing import List
from httpx import AsyncClient, AsyncHTTPTransport
import json
import os
from selectolax.parser import HTMLParser
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
PROXY_URL = os.getenv("PROXY_URL")
MAX_RETRIES = 3  # Number of retries for failed requests

async def scrape_listings():
    """
    Scrape all listing URLs from the website with asynchronous requests.
    """
    base_url = "https://www.websiteclosers.com/businesses-for-sale/"
    page_number = 1
    urls = []

    while True:
        print(f"Scraping page {page_number}...")

        url = base_url if page_number == 1 else f"{base_url}page/{page_number}/"

        for attempt in range(MAX_RETRIES):
            try:
                # Set up proxy transport
                transport = AsyncHTTPTransport(proxy=PROXY_URL)
                async with AsyncClient(transport=transport) as client:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"Successfully fetched page {page_number}")
                        break
                    else:
                        print(f"Failed to fetch page {page_number}. Status: {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)  # Wait before retrying
        else:
            print(f"Max retries reached for page {page_number}. Stopping pagination.")
            break

        # Parse response using Selectolax
        html = HTMLParser(response.text)
        listings = html.css("div.post_item")

        if not listings:
            print("No more listings found. Exiting...")
            break

        # Extract URLs
        for listing in listings:
            link_node = listing.css_first("a.post_thumbnail")
            link = link_node.attributes.get("href") if link_node else None
            if link and link not in urls:
                urls.append(link)

        print(f"Found {len(listings)} listings on page {page_number}.")
        page_number += 1

    save_to_json(urls, "listings.json")
    print(f"Scraped {len(urls)} total listings saved to 'listings.json'.")

def save_to_json(data: List[str], file_path: str):
    """
    Save data to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} listings to {file_path}.")

if __name__ == "__main__":
    asyncio.run(scrape_listings())
