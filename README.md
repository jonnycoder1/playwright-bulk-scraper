# playwright-bulk-scraper

## Purpose
This Python module provides an asynchronous way to make bulk web scraping requests using
Playwright and optionally leveraging Browserless.io service. A single browser instance 
can use multiple pages to make simultaneous requests, or use multiple browser instances!

## How to Use
### Installation
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### Usage
```python
import asyncio
import os
from bulk_scraper.scraper import Scraper


async def process_scraped_url(url, error, content):
    """Callback function to process result of each URL"""
    if error:
        print(f"failed to parse {url} with error {error}")
    else:
        print(f"url success: {url}, content: {content[0:30]}")
    
async def main():
    url_queue = asyncio.Queue()
    test_url = "https://news.ycombinator.com/"
    num_urls = 10

    for _ in range(num_urls):
        await url_queue.put(test_url)
    
    token = os.getenv("BROWSERLESS_TOKEN")
    scraper = Scraper(browserless_token=token, page_limit=5)
    await scraper.run(url_queue=url_queue, callback=process_scraped_url)
    
if __name__ == '__main__':
    asyncio.run(main())
```

### Tests
```
cd tests
docker-compose build --no-cache
docker-compose up
```

## Benchmarks
100 Wikipedia articles were scraped in approximately 25 seconds using a single process and a 
single browser instance, with 5 simultaneous pages connected to Browserless.io.

The following table provides a rough estimate comparing the costs of web scraping URLs. 
The 'Price Per URL' and 'Price Per 1,000,000 URLs' are extrapolated figures.

Real-world implications of scraping 1 million URLs involve many more complications, including 
but not limited to:
* Mitigating anti-bot protection through the use of anti-captcha techniques, proxies, and varied user agents
* Implementing rate limits for frequent requests to a single domain
* Managing long-running sessions


## Price Comparisons
| Service                                  | Pricing                                                  | Price Per URL          | Price Per 1,000,000 URLs | Reference                            |
|------------------------------------------|----------------------------------------------------------|------------------------|--------------------------|--------------------------------------|
| playwright-bulk-scraper + browserless.io | $50/mo 40000 units  optimized (100 req/unit)             | $0.0000125 per request | $12.50                   | https://www.browserless.io/pricing/  |
| browserless.io                           | $50/mo 40000 units                                       | $0.00125 per request   | $1250                    | https://www.browserless.io/pricing/  |
| scrapingfish.com                         | $0.002 per request                                       | $0.002 per request     | $2000                    | https://scrapingfish.com/#pricing    |
| scrapingbee.com                          | $49/mo 150,000 credits  (at least 5 credits per request) | $0.0016666 per request | $1666.6                  | https://www.scrapingbee.com/#pricing |


## Misc
Developed by Jon Olson [**@jonnycoder1**](https://github.com/jonnycoder1)

Website: https://www.jon-olson.com
