import asyncio
from typing import List
from httpx import AsyncClient, AsyncHTTPTransport
from selectolax.parser import HTMLParser
import json
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()
PROXY_URL = os.getenv("PROXY_URL")
MAX_RETRIES = 3  # Number of retries for failed requests

async def scrape_all_details():
    """
    Scrape details for all listings from the JSON file.
    """
    input_file = "listings.json"
    output_file = "details.json"

    # Load URLs from the JSON file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found. Run 'listings_scrape.py' first.")
    with open(input_file, "r", encoding="utf-8") as f:
        urls = json.load(f)

    scraped_details = []

    # Scrape details for each URL
    for url in urls:
        print(f"Scraping details for URL: {url}")

        for attempt in range(MAX_RETRIES):
            try:
                # Set up proxy transport
                transport = AsyncHTTPTransport(proxy=PROXY_URL)
                async with AsyncClient(transport=transport) as client:
                    response = await client.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"Successfully fetched details for {url}")
                        break
                    else:
                        print(f"Failed to fetch details for {url}. Status: {response.status_code}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
            await asyncio.sleep(1)  # Wait before retrying
        else:
            print(f"Max retries reached for {url}. Skipping...")
            continue

        html = HTMLParser(response.text)
        details = extract_details(html, url)
        if details:
            scraped_details.append(details)

    save_to_json(scraped_details, output_file)
    print(f"Scraped details for {len(scraped_details)} listings saved to '{output_file}'.")

def extract_details(html: HTMLParser, url: str) -> dict:
    """
    Extract details from a single listing page.
    """
    try:
        # Extract title
        title_node = html.css_first("h1")
        title = title_node.text(strip=True) if title_node else None

        # Extract description
        description_container = html.css_first("div.wysiwyg.cfx")
        description = (
            "\n".join(p.text(strip=True) for p in description_container.css("p"))
            if description_container
            else None
        )

        # Extract other details
        asking_price = extract_flex_detail(html, "Asking Price")
        cash_flow = extract_flex_detail(html, "Cash Flow")
        gross_income = extract_flex_detail(html, "Gross Income")
        year_established = extract_flex_detail(html, "Year Established")
        employees = extract_flex_detail(html, "Employees")

        return {
            "url": url,
            "title": title,
            "detail_description": description,
            "asking_price": asking_price,
            "cash_flow": cash_flow,
            "gross_income": gross_income,
            "year_established": year_established,
            "employees": employees,
        }
    except Exception as e:
        print(f"Error extracting details for {url}: {e}")
        return {}

def extract_flex_detail(html: HTMLParser, label: str) -> str:
    """
    Extract a specific detail (e.g., Asking Price) from the HTML page.
    """
    lines = html.css("div.line.flex")
    for line in lines:
        label_node = line.css_first("div.col-6.left")
        value_node = line.css_first("div.col-6.right")
        if label_node and value_node and label_node.text(strip=True) == label:
            return value_node.text(strip=True)
    return None

def save_to_json(data: List[dict], file_path: str):
    """
    Save data to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} records to {file_path}.")

if __name__ == "__main__":
    asyncio.run(scrape_all_details())
