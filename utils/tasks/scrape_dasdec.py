""" Scrapes all DASDECs as defined in creds.json """
# ----- 3RD PARTY IMPORT -----
from playwright.async_api import async_playwright

# ----- BUILT IN IMPORTS -----
from typing import List, Tuple
import asyncio

# ----- PROJECT IMPORTS -----
from utils.eas_parse.DasdecScraper import DasdecScraper


# async def scrape(dasdec: dict) -> Tuple[int, str]:
#     """ Scrape content from a specific DASDEC """
#     async with async_playwright() as playwright:
#         scraper = DasdecScraper(playwright, **dasdec)
#
#         return await scraper.scrape()
    

async def scrape_all(dasdecs: List) -> Tuple:
    """ Gathers data from list of DASDECs """  
    # create playwright context
    async with async_playwright() as playwright:
        # instantiate scraper objects
        scrapers = create_scrapers(playwright, dasdecs)
        
        # call scrape method
        tasks = [scraper.scrape() for scraper in scrapers]
        
        return await asyncio.gather(*tasks)


def create_scrapers(playwright: async_playwright,
                    dasdecs: List[dict]) -> List[DasdecScraper]:
    """ Instantiate DASDEC Scraper from Playwright instance """
    return [DasdecScraper(playwright, **dasdec) for dasdec in dasdecs]


def run_async_scraper(dasdecs: List[dict]) -> List[Tuple[int, str]]:
    """ """
    return asyncio.run(scrape_all(dasdecs))
