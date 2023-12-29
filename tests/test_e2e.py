import asyncio
import logging
from bulk_scraper.scraper import Scraper
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def process_scraped_url(url, error, content):
    if error:
        logger.info(f"failed to parse {url} with error {error}")
        return
    logger.info(f"url success: {url}, content: {content[0:30]}")


async def main():
    try:
        logger.info("begin main")
        # Populate asynchronous queue
        url_queue = asyncio.Queue()
        urls = ["https://news.ycombinator.com/"] * 10
        for url in urls:
            await url_queue.put(url)

        scraper = Scraper(browserless_token="end2end-test-token",
                          browserless_url="ws://browserless:3000",
                          connect_over_cdp=True,
                          page_limit=5,
                          request_timeout=10000,
                          )
        await scraper.run(url_queue=url_queue, callback=process_scraped_url)
        logger.info("scraper complete")
    except Exception as e:
        logger.exception(e)
        exit(1)

if __name__ == '__main__':
    asyncio.run(main())

