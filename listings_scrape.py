import httpx
from selectolax.parser import HTMLParser
import csv

def scrape_listings():
    url = "https://www.websiteclosers.com/businesses-for-sale/"
    
    # Send a GET request to the website
    response = httpx.get(url)
    print(f"Response Status Code: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch webpage. Status code: {response.status_code}")
    
    # Parse the HTML response
    html = HTMLParser(response.text)
    
    # Find all listing divs
    listings = html.css("div.post_item")
    
    # Extract and print URLs
    urls = []
    for listing in listings:
        link_node = listing.css_first("a.post_thumbnail")
        link = link_node.attributes.get("href") if link_node and "href" in link_node.attributes else None
        if link:
            urls.append(link)
    
    # Print all scraped URLs
    print(f"Total Listings Found: {len(urls)}")
    print("Scraped URLs:")
    for url in urls:
        print(url)
    

     # Save to CSV
    save_to_csv(urls)
    
    # Print total count and all scraped URLs
    print(f"Total Listings Found: {len(urls)}")
    print("Scraped URLs saved to 'listings.csv'.")

def save_to_csv(urls):
    with open("listings.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["websiteclosers.com - Listings URL"])  # Add a header
        for url in urls:
            writer.writerow([url])
            writer.writerow([])
        writer.writerow(["Total Listings", len(urls)])
    return urls

if __name__ == "__main__":
    scraped_urls = scrape_listings()
scrape_listings()