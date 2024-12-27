import httpx
import asyncio
# Proxy URL
PROXY_URL = "http://zuyarehm-rotate:xxodprhhcpjr@p.webshare.io:80/"
# URL to fetch public IP
IP_CHECK_URL = "https://api.ipify.org?format=json"
async def check_proxy_rotation():
    async with httpx.AsyncClient(
        timeout=10,
        transport=httpx.AsyncHTTPTransport(proxy=PROXY_URL)
    ) as client:
        for i in range(5):  # Test with 5 requests
            try:
                response = await client.get(IP_CHECK_URL)
                response.raise_for_status()
                ip_data = response.json()
                print(f"Request {i+1}: Public IP -> {ip_data['ip']}")
            except Exception as e:
                print(f"Error during request {i+1}: {e}")
# Run the function
asyncio.run(check_proxy_rotation())