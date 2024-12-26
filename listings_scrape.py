import httpx
from selectolax.parser import HTMLParser
import json
import os
import asyncio


async def fetch_page(url, client):
    """Fetch a single page asynchronously."""
    try:
        response = await client.get(url)
        print(f"Response Status Code for {url}: {response.status_code}")
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


async def scrape_listings():
    base_url = "https://www.websiteclosers.com/businesses-for-sale/"
    urls = []
    page_number = 1

    async with httpx.AsyncClient() as client:
        while True:
            print(f"Scraping page {page_number}...")
            # Generate URL for the current page
            url = base_url if page_number == 1 else f"{base_url}page/{page_number}/"
            html_content = await fetch_page(url, client)

            if not html_content:
                print(f"Page {page_number} not found or no more pages. Stopping pagination.")
                break

            # Parse the HTML response
            html = HTMLParser(html_content)

            # Find all listing divs
            listings = html.css("div.post_item")
            if not listings:
                print(f"No listings found on page {page_number}. Ending scraping.")
                break

            # Extract URLs
            for listing in listings:
                link_node = listing.css_first("a.post_thumbnail")
                link = link_node.attributes.get("href") if link_node and "href" in link_node.attributes else None
                if link and link not in urls:
                    urls.append(link)

            print(f"Found {len(listings)} listings on page {page_number}.")
            page_number += 1

    # Save all URLs to JSON
    save_to_json(urls)
    print(f"Scraped {len(urls)} total listings across all pages.")
    print("Scraped URLs saved to 'listings_with_pagination.json'.")


def save_to_json(urls):
    file_path = "listings_with_pagination.json"

    # Read existing URLs if the file exists
    existing_urls = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as jsonfile:
            existing_urls = set(json.load(jsonfile))

    # Merge new URLs with existing ones
    new_urls = [url for url in urls if url not in existing_urls]
    all_urls = list(existing_urls | set(new_urls))

    # Write all URLs to the JSON file
    with open(file_path, "w", encoding="utf-8") as jsonfile:
        json.dump(all_urls, jsonfile, indent=4)

    print(f"Appended {len(new_urls)} new listings to the JSON file. Total listings now: {len(all_urls)}.")


if __name__ == "__main__":
    asyncio.run(scrape_listings())
