import asyncio
import json
from httpx import AsyncClient
from parsel import Selector

client = AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.tripadvisor.com/",
    },
    follow_redirects=True,
    timeout=15.0
)


async def scrape_hotel_links(location_url: str) -> None:
    """Scrape hotel links from a location page and save them to a file."""
    response = await client.get(location_url)
    if response.status_code != 200:
        print(f"Failed to fetch location page {location_url}, status code: {response.status_code}")
        return

    selector = Selector(response.text)
    hotel_links = [
        f"https://www.tripadvisor.com{hotel.attrib.get('href')}"
        for hotel in selector.css("div.jsTLT.K a.BMQDV._F")
        if hotel.attrib.get("href", "").startswith("/Hotel_Review")
    ]

    # Save links to JSON
    with open("hotel_links.json", "w") as f:
        json.dump(hotel_links, f, indent=2)

    print(f"Scraped {len(hotel_links)} hotel links and saved to 'hotel_links.json'.")


async def main():
    location_url = "https://www.tripadvisor.com/Hotels-g189400-Athens_Attica-Hotels.html"
    await scrape_hotel_links(location_url)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
