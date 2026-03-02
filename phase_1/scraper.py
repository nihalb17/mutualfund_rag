import httpx
from bs4 import BeautifulSoup
import json
import os
import time

FUND_LINKS = [
    "https://groww.in/mutual-funds/axis-liquid-direct-fund-growth",
    "https://groww.in/mutual-funds/axis-elss-tax-saver-direct-plan-growth",
    "https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-midcap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/axis-focused-direct-plan-growth"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def scrape_fund(url):
    print(f"Scraping {url}...")
    try:
        response = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        fund_name = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Fund"
        
        # Groww often stores key data in a JSON script tag (__NEXT_DATA__)
        # This is more reliable than parsing HTML tags which change classes
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        
        data = {
            "url": url,
            "fund_name": fund_name,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "raw_text": soup.get_text(separator="\n", strip=True) # Fallback for RAG
        }
        
        if next_data_script:
            try:
                js_data = json.loads(next_data_script.string)
                # Attempt to extract structured data from NEXT_DATA if needed
                # For Phase 1, we will keep the full text for RAG processing
                data["structured_data"] = js_data
            except Exception as e:
                print(f"Error parsing NEXT_DATA for {url}: {e}")

        # Save as JSON for structured use
        filename = url.split('/')[-1] + ".json"
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        # Also save as Markdown for RAG context
        md_filename = url.split('/')[-1] + ".md"
        with open(os.path.join(OUTPUT_DIR, md_filename), "w", encoding='utf-8') as f:
            f.write(f"# {fund_name}\n\nSource: {url}\n\n")
            f.write(data["raw_text"])

        print(f"Successfully scraped {fund_name}")
        return True
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return False

def main():
    success_count = 0
    for link in FUND_LINKS:
        if scrape_fund(link):
            success_count += 1
        time.sleep(2) # Be polite
    
    print(f"\nScraping complete. Successfully scraped {success_count}/{len(FUND_LINKS)} funds.")

if __name__ == "__main__":
    main()
