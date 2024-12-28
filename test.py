# Script with required changes for Nirav
from httpx import AsyncClient, AsyncHTTPTransport
from selectolax.parser import HTMLParser
# from src.scraper.proxy_config import PROXY_URL


async def get_all_listings(max_retries: int = 3):
    """
    Scrape all listings URLs from the paginated website.
    """
    page_number = 1
    listings_urls = []

    while True:
        url = f"https://www.websiteclosers.com/businesses-for-sale/page/{page_number}/"
        print(f"Fetching page {page_number}...")

        for attempt in range(max_retries):
            try:
                transport = AsyncHTTPTransport(proxy="PROXY_URL")
                async with AsyncClient(transport=transport, follow_redirects=True) as client:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"Successfully fetched page {page_number}")
                        break
                    elif response.status_code in {301, 302}:
                        print(f"Redirected to {response.headers.get('Location')}")
                    else:
                        print(f"Failed to fetch page {page_number}. Status: {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for page {page_number}: {e}")
            await asyncio.sleep(1)  # Backoff before retrying
        else:
            print(f"Max retries reached for page {page_number}. Stopping pagination.")
            return listings_urls

        # Parse response for listings
        html = HTMLParser(response.text)
        listings = html.css("div.post_item")

        if not listings:
            print(f"No listings found on page {page_number}. Exiting pagination...")
            break

        for listing in listings:
            link_node = listing.css_first("a.post_thumbnail")
            link = link_node.attributes.get("href") if link_node else None
            if link and link not in listings_urls:
                listings_urls.append(link)

        print(f"Found {len(listings)} listings on page {page_number}.")
        page_number += 1  # Move to the next page

    print(f"Scraped a total of {len(listings_urls)} listings.")
    return listings_urls

# Example usage
if __name__ == "__main__":
    import asyncio
    results = asyncio.run(get_all_listings())
    print("Scraped URLs:", results)
