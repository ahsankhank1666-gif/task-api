import os
import re
import time
import json
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional
from pydantic import BaseModel, HttpUrl, ValidationError

# --- Stage 4: Pydantic Schema Definition ---
class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str

# --- Stage 1 & 5: Polite Fetching & Cache Management ---
def fetch_html(url, file_path, stats):
    cache_dir = "../cache"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(file_path):
        stats["cache_hits"] += 1
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read(), 200

    stats["pages_fetched"] += 1
    time.sleep(0.5)  # Polite delay
    
    headers = {"User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/MuhammadAhsanKhan)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # Retry once on 5xx server errors or timeouts (Stage 5)
        if response.status_code >= 500:
            time.sleep(1.0)
            response = requests.get(url, headers=headers, timeout=10)
            
        if response.status_code == 200:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return response.text, 200
        else:
            return None, response.status_code
            
    except Exception as e:
        return None, 500

# --- Stage 2: Page Discovery ---
def get_three_pages_of_links(stats):
    current_url = "https://books.toscrape.com/catalogue/page-1.html"
    all_book_links = []
    pages_visited = 0
    
    while pages_visited < 3 and current_url:
        pages_visited += 1
        file_path = f"../cache/catalogue-page-{pages_visited}.html"
        
        html_content, status = fetch_html(current_url, file_path, stats)
        if not html_content:
            break
            
        soup = BeautifulSoup(html_content, "html.parser")
        
        articles = soup.find_all("article", class_="product_pod")
        for article in articles:
            link = article.find("h3").find("a")["href"]
            full_url = urljoin(current_url, link)
            all_book_links.append(full_url)
            
        next_button = soup.find("li", class_="next")
        if next_button:
            next_link = next_button.find("a")["href"]
            current_url = urljoin(current_url, next_link)
        else:
            current_url = None

    unique_links = list(set(all_book_links))
    print(f"catalogue_pages = {pages_visited}, discovered = {len(all_book_links)}, unique_urls = {len(unique_links)}")
    return unique_links

# --- Stage 3 & 4: Data Extraction & Normalization ---
def extract_book_details(book_url, stats):
    book_id = book_url.split("/")[-2] 
    file_path = f"../cache/{book_id}.html"
    
    html_content, status_code = fetch_html(book_url, file_path, stats)
    if not html_content:
        stats["failed_pages"] += 1
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    title = soup.find("h1").text if soup.find("h1") else None
    
    price_p = soup.find("p", class_="price_color")
    price_text = price_p.text if price_p else ""
    
    # Clean price_text into price_gbp numeric float (Stage 4)
    price_match = re.search(r"\d+\.\d+", price_text)
    price_gbp = float(price_match.group()) if price_match else 0.0
    
    avail_p = soup.find("p", class_="instock availability")
    availability_text = avail_p.text.strip() if avail_p else ""
    
    rating_p = soup.find("p", class_="star-rating")
    rating_text = rating_p["class"][1] if rating_p else ""
    
    desc_heading = soup.find("div", id="product_description")
    description = desc_heading.find_next_sibling("p").text if desc_heading else None
    
    raw_record = {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": "https://books.toscrape.com/catalogue/page-1.html",
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    return raw_record

# --- Main Pipeline ---
def run_pipeline():
    start_time = datetime.datetime.now(datetime.timezone.utc)
    
    stats = {
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0
    }
    
    links = get_three_pages_of_links(stats)
    
    # Stage 5 Test: Add one fake URL to prove resilience against 404 failure
    fake_url = "https://books.toscrape.com/catalogue/broken-fake-book_9999/index.html"
    links.append(fake_url)
    
    valid_books = []
    errors = []
    
    print("\nProcessing book pages...")
    for link in links:
        raw_record = extract_book_details(link, stats)
        if raw_record:
            try:
                # Stage 4 Schema Validation
                validated_record = BookRecord(**raw_record)
                # Convert validated model to standard dictionary
                valid_books.append(json.loads(validated_record.model_dump_json()))
                stats["valid_records"] += 1
            except ValidationError as ve:
                stats["invalid_records"] += 1
                errors.append({"url": link, "error": str(ve)})
                
    end_time = datetime.datetime.now(datetime.timezone.utc)
    duration_seconds = round((end_time - start_time).total_seconds(), 2)
    
    # Ensure output folder exists
    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save output files
    with open(f"{output_dir}/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_books, f, indent=2)
        
    with open(f"{output_dir}/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2)
        
    run_report = {
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration_seconds": duration_seconds,
        "pages_fetched": stats["pages_fetched"],
        "cache_hits": stats["cache_hits"],
        "valid_records": stats["valid_records"],
        "invalid_records": stats["invalid_records"],
        "failed_pages": stats["failed_pages"]
    }
    
    with open(f"{output_dir}/run-report.json", "w", encoding="utf-8") as f:
        json.dump(run_report, f, indent=2)
        
    print("\n--- Pipeline Completed ---")
    print(json.dumps(run_report, indent=2))

if __name__ == "__main__":
    run_pipeline()