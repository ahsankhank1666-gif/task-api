## Target Classification
* **Target:** Books to Scrape (toscrape.com)
* **Scope:** The first 3 catalogue pages only.
* **Data Collected:** Book titles, prices, availability, ratings, and descriptions.
* **Why it is appropriate:** The site explicitly states it is a sandbox built for scraping practice.
* **Robots.txt check:** Checked https://books.toscrape.com/robots.txt and received a 404 error (no robots file found).
* I will not reuse this code on another site without checking its rules and terms first.
## Execution
**Lane:** Python (Requests, BeautifulSoup, Pydantic)
**Run Command:** `python src/main.py`
**Note on Browser Automation:** A headless browser like Playwright was unnecessary here because all required data is present in the initial HTML payload sent by the server, meaning rendering JavaScript would only add unnecessary computing cost.

## Politeness Rules & Schema
* **Rules Followed:** Sends a custom user-agent with contact info, implements a 500ms delay between live requests, enforces a 10-second timeout, and reads from a local cache during development.
* **Limitation:** The scraper relies heavily on specific HTML class names; if the site owner changes the frontend structure, the BeautifulSoup selectors will break.
* **Ethics Note:** Always check a site's terms and `robots.txt` before automating. Collect only necessary public data, avoid hammering servers with concurrent requests, and never bypass authentication to scrape private data.
* **Schema:** `BookRecord(title: str, product_url: HttpUrl, price_text: str, price_gbp: float, availability_text: str, rating_text: str, description: Optional[str], source_page: HttpUrl, fetched_at: str)`.

## Proof of Run
```json
{
  "start_time": "2026-09-24T08:12:23Z",
  "duration_seconds": 3.83,
  "pages_fetched": 1,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}

<img width="1838" height="1015" alt="image" src="https://github.com/user-attachments/assets/821c151b-66c2-46e5-a9e8-54442ccfa5db" />

