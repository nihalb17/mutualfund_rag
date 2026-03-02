import os
import json
import pytest

DATA_DIR = "phase_1/data/raw"

def test_scraping_completion():
    """Verify all 7 target URLs are successfully scraped."""
    if not os.path.exists(DATA_DIR):
        pytest.skip("Data directory not found. Run scraper first.")
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    assert len(files) == 7

def test_data_integrity():
    """Ensure generated JSON files contain essential fields."""
    if not os.path.exists(DATA_DIR):
        pytest.skip("Data directory not found. Run scraper first.")
        
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding='utf-8') as f:
                data = json.load(f)
                assert "url" in data
                assert "fund_name" in data
                assert "raw_text" in data
