import asyncio
import aiofiles
import logging
import os
import time
from bulk_scraper.scraper import Scraper
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def process_scraped_url(url, error, content):
    fn = url.replace("/", "").replace(":", "-")
    fn = fn + ".html"
    # Log error and save to .error file
    if error:
        logger.info(f"failed to parse {url} with error {error}")
        fn += ".error"
        content = error
    # Save each url and result to a file
    with open(fn, "w") as file:
        file.write(content)
    async with aiofiles.open(fn, mode='w') as file:
        await file.write(content)


async def main():
    try:
        logger.info("begin main")
        start_time = time.time()

        # Populate asynchronous queue
        url_queue = asyncio.Queue()
        with open("urls.txt", "r") as file:
            for line in file:
                await url_queue.put(line.strip())

        # Call Scraper
        token = os.getenv("BROWSERLESS_TOKEN")
        scraper = Scraper(browserless_token=token, page_limit=5)
        await scraper.run(url_queue=url_queue, callback=process_scraped_url)
        logger.info("scraper complete")

        # Log time taken
        end_time = time.time()
        duration = end_time - start_time
        print(f"The scraper took {duration} seconds to run.")
    except Exception as e:
        logger.exception(e)
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())

