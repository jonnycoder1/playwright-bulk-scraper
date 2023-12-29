FROM python:3.11.7-slim-bookworm

WORKDIR /etc/playwright-bulk-scraper
ENV PYTHONPATH="/etc/playwright-bulk-scraper:$PYTHONPATH"
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
WORKDIR /etc/playwright-bulk-scraper/tests

CMD ["python", "test_e2e.py"]
