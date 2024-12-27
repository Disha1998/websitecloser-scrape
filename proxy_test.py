import os
import asyncio
from httpx import AsyncClient, AsyncHTTPTransport
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PROXY_URL = os.getenv("PROXY_URL")  # Ensure this is set in your .env file
IP_CHECK_URL = "https://api.ipify.org?format=json"  # API to fetch public IP

async def test_proxy():
    """Check if the proxy is working."""
    try:
        if not PROXY_URL:
            raise ValueError("Proxy URL not set in the environment variables.")

        print(f"Testing Proxy: {PROXY_URL}")

        # Set up the transport with proxy
        transport = AsyncHTTPTransport(proxy=PROXY_URL)

        # Use AsyncClient with the configured transport
        async with AsyncClient(transport=transport) as client:
            # Make a request to check IP
            response = await client.get(IP_CHECK_URL)
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
            data = response.json()

            print("Proxy is working! Here's the IP info:")
            print(data)  # Display IP info to verify the proxy
    except Exception as e:
        print(f"Proxy test failed: {e}")

# Run the proxy test
if __name__ == "__main__":
    asyncio.run(test_proxy())
