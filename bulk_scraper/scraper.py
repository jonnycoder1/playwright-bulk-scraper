import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class Scraper:
    """A class for performing bulk web scraping using Browserless.io service.

    This class provides an interface to make bulk web scraping requests using
    Playwright and leveraging Browserless.io service. Given an asyncio Queue,
    a single browser instance will scrape using multiple pages until the queue
    is empty.

    It optimizes the unit usage of the service by issuing as many requests
    using a single Chromium browser instance with a user-defined number of
    browser pages. According to https://www.browserless.io/pricing, a unit
    is a block of browser time up to 30 seconds.

    Attributes:
        browserless_token: Your API token/key for Browserless.io
        browserless_url: A string for remote URL to connect to Browserless.io
                         (default 'wss://chrome.browserless.io/playwright')
        connect_over_cdp: A boolean for connecting via Playwright Chrome
                          DevTools
        page_limit: An integer for number of simultaneous Chrome Pages to use
                    (default 5)
        request_timeout: An integer, in ms, to timeout for each url
                         (default 10000)
    """
    def __init__(self,
                 browserless_token,
                 browserless_url="wss://chrome.browserless.io/playwright",
                 connect_over_cdp=False,
                 page_limit=5,
                 request_timeout=10000):
        self.page_limit = page_limit
        self.request_timeout = request_timeout
        self.browserless_token = browserless_token
        self.browserless_url = browserless_url
        self.connect_over_cdp = connect_over_cdp
        self.playwright = None
        self.browser = None
        self.pages = []

    async def start_browser(self):
        """Starts the browser and initializes pages."""
        url = f"{self.browserless_url}" \
              f"?token={self.browserless_token}" \
              f"&headless=false"
        logger.info(f"start_browser begin for url: {url}")
        self.playwright = await async_playwright().start()

        if self.connect_over_cdp:
            self.browser = await self.playwright.chromium.connect_over_cdp(endpoint_url=url)
        else:
            self.browser = await self.playwright.chromium.connect(ws_endpoint=url)

        logger.info("browser connected")
        for i in range(self.page_limit):
            page = await self.browser.new_page()
            logger.info(f"start_browser created page {i}")
            self.pages.append((page, i))

    async def stop_browser(self):
        logger.info("stop browser begin")
        for page, page_id in self.pages:
            logger.info(f"closing page_id {page_id}")
            await page.close()
        if self.browser:
            await self.browser.close()

    async def scrape_url(self, page, page_id, url):
        """Scrapes a single URL using a given page."""
        try:
            logger.info(f"scrape_url begin for page_id {page_id}, url {url}")
            await page.goto(url, timeout=self.request_timeout)
            content = await page.content()
            return url, None, content
        except Exception as e:
            logger.exception(f"Error scraping {url}: {e}")
            return url, str(e), None

    async def page_process_queue(self, url_queue, page, page_id, callback):
        """A page instance continuously scrape urls from the queue."""
        logger.info(f"page_process_queue begin with page_id {page_id} "
                    f"and url_queue length of {url_queue.qsize()}")
        while True:
            if url_queue.empty():
                logger.info(f"page_process_queue queue empty for page_id {page_id}")
                break
            url = await url_queue.get()
            url, error, content = await self.scrape_url(page=page, page_id=page_id, url=url)
            await callback(url, error, content)

    async def run(self, url_queue, callback):
        """Main method to process and scrape URLs from the queue."""
        logger.info("run begin")
        await self.start_browser()
        logger.info("about to run tasks")
        tasks = []
        for page, page_id in self.pages:
            task = asyncio.create_task(self.page_process_queue(url_queue, page, page_id, callback))
            tasks.append(task)

        await asyncio.gather(*tasks)
        logger.info("all tasks completed")
        await self.stop_browser()
        logger.info("browser stopped")
