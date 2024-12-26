import httpx
from selectolax.parser import HTMLParser
import json
import asyncio
import os


async def fetch_page(url, client):
    """Fetch a single page asynchronously."""
    try:
        response = await client.get(url, timeout=10)  # Set a timeout for requests
        print(f"Response Status Code for {url}: {response.status_code}")
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}. HTTP Status Code: {response.status_code}")
    except httpx.RequestError as exc:
        print(f"Error fetching {url}: {exc}")
    return None


async def scrape_all_details():
    # Input file containing listing URLs
    input_file = "listings_with_pagination.json"
    output_file = "details.json"

    # Read listing URLs from the JSON file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} not found. Please scrape listings first.")
    with open(input_file, "r", encoding="utf-8") as f:
        urls = json.load(f)

    # Scraped details storage
    scraped_details = []

    async with httpx.AsyncClient() as client:
        for url in urls:
            print(f"Scraping details for URL: {url}")
            html_content = await fetch_page(url, client)

            if not html_content:
                print(f"Skipping {url} due to fetch error.")
                continue

            # Parse the HTML response
            html = HTMLParser(html_content)

            # Extract the title
            title_node = html.css_first("h1")
            title = title_node.text(strip=True) if title_node else None

            # Extract detailed description
            description_container = html.css_first("div.wysiwyg.cfx")
            description = (
                "\n".join(p.text(strip=True) for p in description_container.css("p"))
                if description_container
                else None
            )

            # Extract other details using the "line flex" structure
            asking_price = extract_flex_detail(html, "Asking Price")
            cash_flow = extract_flex_detail(html, "Cash Flow")
            gross_income = extract_flex_detail(html, "Gross Income")
            year_established = extract_flex_detail(html, "Year Established")
            employees = extract_flex_detail(html, "Employees")

            # Append scraped details
            scraped_details.append({
                "url": url,
                "title": title,
                "detail_description": description,
                "asking_price": asking_price,
                "cash_flow": cash_flow,
                "gross_income": gross_income,
                "year_established": year_established,
                "employees": employees
            })

    # Save all details to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scraped_details, f, ensure_ascii=False, indent=4)

    print(f"Scraped details for {len(scraped_details)} listings saved to {output_file}.")


def extract_flex_detail(html, label):
    """Extracts the value for a specific label like 'Asking Price' or 'Year Established'."""
    lines = html.css("div.line.flex")
    for line in lines:
        label_node = line.css_first("div.col-6.left")
        value_node = line.css_first("div.col-6.right")
        if label_node and value_node and label_node.text(strip=True) == label:
            return value_node.text(strip=True)
    return None


if __name__ == "__main__":
    asyncio.run(scrape_all_details())
