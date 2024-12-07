from typing import List, Dict, Optional
import asyncio
import json
import random
import time
from httpx import AsyncClient, Response
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


def parse_hotel_page(result: Response) -> Dict:
    """Parse hotel data from hotel pages"""
    selector = Selector(result.text)
    basic_data = json.loads(selector.xpath("//script[contains(text(),'aggregateRating')]/text()").get())
    description = selector.css("div.fIrGe._T::text").get()
    amenities = []
    for feature in selector.xpath("//div[contains(@data-test-target, 'amenity')]/text()"):
        amenities.append(feature.get())

    return {
        "basic_data": basic_data,
        "description": description,
        "features": amenities
    }


async def scrape_hotel(url: str) -> Dict:
    """Scrape hotel data and reviews"""
    first_page = await client.get(url)
    if first_page.status_code == 403:
        print("Request blocked, retrying...")
        await asyncio.sleep(random.uniform(5, 10))  # Sleep to avoid blocking
        return await scrape_hotel(url)  # Retry the request
    hotel_data = parse_hotel_page(first_page)
    print(f"Scraped one hotel data.")
    return hotel_data


async def scrape_hotels(urls: List[str]) -> List[Dict]:
    """Scrape data for multiple hotels"""
    all_hotel_data = []
    for url in urls:
        hotel_data = await scrape_hotel(url)
        all_hotel_data.append(hotel_data)
    return all_hotel_data


async def main():
    # Read list of urls from hotels_links.json
    with open("hotel_links.json", "r") as f:
        hotel_urls = json.load(f)

    hotel_data = await scrape_hotels(hotel_urls)

    # Create and save data in JSON
    with open("hotel_data.json", "w") as f:
        json.dump(hotel_data, f, indent=2)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
