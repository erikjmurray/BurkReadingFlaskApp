""" Scrapes all DASDECs as defined in creds.json """
# ----- 3RD PARTY IMPORT -----
from playwright.async_api import async_playwright

# ----- BUILT IN IMPORTS -----
from typing import List, Tuple
import asyncio
import json
import os

# ----- PROJECT IMPORTS -----
from utils.eas_parse.DasdecScraper import DasdecScraper
from utils.tasks.parse_dasdec_html import parse

def read_creds_file() -> List[dict]:
    """ Read JSON data for DASDEC login """
    creds_path = os.path.join(os.getcwd(), 'creds.json')
    with open(creds_path, 'r') as f:
        content = f.read()
        
    return json.loads(content)


##def write_to_file(name: str, content: str) -> None:
##    """ Write content to txt file in separate folder """
##    target_dir = os.path.join(os.getcwd(), 'ScrapedLogs')
##    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
##    filename = f"{timestamp}_{name.replace(' ', '_')}_eas_report.txt"
##
##    # Check if the directory exists and create it if it doesn't
##    if not os.path.exists(target_dir):
##        os.makedirs(target_dir)
##
##    # write to file
##    with open(os.path.join(target_dir, filename), 'w') as f:
##        f.write(content)
##    return


async def scrape(dasdec: dict) -> Tuple[int, str]:
    """ Scrape content from a specific DASDEC """
    async with async_playwright() as playwright:
        scraper = DasdecScraper(playwright, **dasdec)

        return await scraper.scrape()
    

async def scrape_all(dasdecs: List) -> List[Tuple[int, str]]:
    """ Gathers data from list of DASDECs """  
    # create playwright context
    async with async_playwright() as playwright:
        # instantiate scraper objects
        scrapers = create_scrapers(playwright, dasdecs)
        
        # call scrape method
        tasks = [scraper.scrape() for scraper in scrapers]
        
        # get scraped content
        return await asyncio.gather(*tasks)


def create_scrapers(playwright: async_playwright,
                    dasdecs: List[dict]) -> List[DasdecScraper]:
    return [DasdecScraper(playwright, **dasdec) for dasdec in dasdecs]


def main():
    dasdecs = read_creds_file()
    
##    response_code, result = asyncio.run(scrape(dasdecs[-2]))
##    if response_code == 200:
##        parse(result)
##    else:
##        print(f"{response_code}: {result}")
    
    results = asyncio.run(scrape_all(dasdecs))
    for i, (response_code, result) in enumerate(results):
        print("\n******************\n", dasdecs[i]["name"], "\n******************\n")
        if response_code == 200:
            parse(result)
        else:
            print(f"{response_code}: {result}")


if __name__ == "__main__":
    main()
