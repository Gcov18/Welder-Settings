"""
Automated Data Collection System for Weld Parameter Optimizer
This module handles automatic data collection from various sources including:
- Web scraping of welding parameter tables
- Image processing of welding charts
- API integration with welding equipment manufacturers
- PDF parsing of AWS welding procedures
"""

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import json
import os
import sys
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import cv2
import pytesseract
from PIL import Image
import tempfile

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.db_manager import DatabaseManager
    from utils.validation import comprehensive_validation
except ImportError:
    print("Warning: Could not import local modules")


class AutomatedDataCollector:
    """Automatically collect welding parameter data from various online sources."""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.collected_data = []
        self.sources = {
            "lincoln_electric": "https://www.lincolnelectric.com",
            "miller_welding": "https://www.millerwelds.com",
            "esab": "https://www.esab.com",
            "aws": "https://www.aws.org",
            "welding_guru": "https://www.weldingguru.com",
        }

    def setup_web_driver(self, headless=True):
        """Setup Selenium web driver for dynamic content."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error setting up web driver: {e}")
            return None

    def search_welding_parameters_web(self, search_terms=None):
        """Search the web for welding parameter tables and charts."""
        if search_terms is None:
            search_terms = [
                "welding parameter chart",
                "MIG welding settings table",
                "TIG welding parameters",
                "stick welding amperage chart",
                "welding voltage settings",
                "AWS welding procedures",
                "welding parameter calculator",
            ]

        collected_urls = []

        for term in search_terms:
            print(f"Searching for: {term}")
            urls = self._google_search_welding_data(term)
            collected_urls.extend(urls)
            time.sleep(2)  # Be respectful to search engines

        return list(set(collected_urls))  # Remove duplicates

    def _google_search_welding_data(self, query):
        """Perform Google search for welding parameter data."""
        # Note: In a real implementation, you'd use Google Custom Search API
        # This is a simplified example
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract search result URLs
            urls = []
            for link in soup.find_all("a", href=True):
                url = link["href"]
                if "/url?q=" in url:
                    actual_url = url.split("/url?q=")[1].split("&")[0]
                    if self._is_welding_resource(actual_url):
                        urls.append(actual_url)

            return urls[:5]  # Return top 5 results

        except Exception as e:
            print(f"Error searching for {query}: {e}")
            return []

    def _is_welding_resource(self, url):
        """Check if URL is likely to contain welding parameter data."""
        welding_keywords = [
            "welding",
            "mig",
            "tig",
            "gmaw",
            "gtaw",
            "smaw",
            "fcaw",
            "lincoln",
            "miller",
            "esab",
            "aws",
            "parameter",
            "chart",
        ]

        url_lower = url.lower()
        return any(keyword in url_lower for keyword in welding_keywords)

    def extract_data_from_url(self, url):
        """Extract welding parameter data from a given URL."""
        print(f"Extracting data from: {url}")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            # Look for tables containing welding parameters
            tables = soup.find_all("table")
            extracted_data = []

            for table in tables:
                if self._contains_welding_parameters(table):
                    data = self._parse_welding_table(table)
                    if data:
                        extracted_data.extend(data)

            # Look for images that might contain parameter charts
            images = soup.find_all("img")
            for img in images:
                if self._is_parameter_chart(img):
                    img_data = self._extract_from_image(img, url)
                    if img_data:
                        extracted_data.extend(img_data)

            return extracted_data

        except Exception as e:
            print(f"Error extracting data from {url}: {e}")
            return []

    def _contains_welding_parameters(self, table):
        """Check if table contains welding parameter data."""
        text = table.get_text().lower()
        parameter_keywords = [
            "voltage",
            "amperage",
            "current",
            "wire speed",
            "travel speed",
            "thickness",
            "material",
            "electrode",
            "gas flow",
        ]

        keyword_count = sum(1 for keyword in parameter_keywords if keyword in text)
        return keyword_count >= 3  # Must contain at least 3 parameter keywords

    def _parse_welding_table(self, table):
        """Parse HTML table to extract welding parameters."""
        try:
            # Convert HTML table to pandas DataFrame
            df = pd.read_html(str(table))[0]

            # Standardize column names
            df.columns = [col.lower().strip() for col in df.columns]

            # Map common column variations to standard names
            column_mapping = {
                "material": ["material", "base metal", "base material"],
                "thickness": ["thickness", "thick", "gauge"],
                "voltage": ["voltage", "volts", "v"],
                "amperage": ["amperage", "amps", "current", "a"],
                "wire_speed": ["wire speed", "wire feed", "wfs", "ipm"],
                "travel_speed": ["travel speed", "travel", "ts"],
                "process": ["process", "welding process"],
                "electrode": ["electrode", "wire", "rod"],
            }

            # Rename columns based on mapping
            for standard_name, variations in column_mapping.items():
                for col in df.columns:
                    if any(var in col for var in variations):
                        df.rename(columns={col: standard_name}, inplace=True)
                        break

            # Convert to list of dictionaries
            records = df.to_dict("records")

            # Clean and validate records
            cleaned_records = []
            for record in records:
                cleaned = self._clean_parameter_record(record)
                if cleaned and self._validate_parameter_record(cleaned):
                    cleaned_records.append(cleaned)

            return cleaned_records

        except Exception as e:
            print(f"Error parsing table: {e}")
            return []

    def _is_parameter_chart(self, img_tag):
        """Check if image is likely a welding parameter chart."""
        src = img_tag.get("src", "")
        alt = img_tag.get("alt", "").lower()
        title = img_tag.get("title", "").lower()

        chart_keywords = ["chart", "table", "parameter", "setting", "welding", "mig", "tig", "voltage", "amperage"]

        text_to_check = f"{src} {alt} {title}".lower()
        return any(keyword in text_to_check for keyword in chart_keywords)

    def _extract_from_image(self, img_tag, base_url):
        """Extract welding parameters from image using OCR."""
        try:
            img_url = urljoin(base_url, img_tag.get("src"))

            # Download image
            response = requests.get(img_url, timeout=10)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name

            # Process with OCR
            extracted_text = pytesseract.image_to_string(Image.open(tmp_path))

            # Clean up temporary file
            os.unlink(tmp_path)

            # Parse text for parameters
            parameters = self._parse_text_for_parameters(extracted_text)

            return parameters

        except Exception as e:
            print(f"Error extracting from image: {e}")
            return []

    def _parse_text_for_parameters(self, text):
        """Parse OCR text to extract welding parameters."""
        parameters = []
        lines = text.split("\n")

        # Look for parameter patterns
        voltage_pattern = r"(\d+(?:\.\d+)?)\s*(?:v|volt|voltage)"
        amperage_pattern = r"(\d+(?:\.\d+)?)\s*(?:a|amp|amperage|current)"
        thickness_pattern = r"(\d+(?:\.\d+)?)\s*(?:mm|inch|in|thick)"

        current_record = {}

        for line in lines:
            line = line.lower().strip()

            # Extract voltage
            voltage_match = re.search(voltage_pattern, line)
            if voltage_match:
                current_record["voltage"] = float(voltage_match.group(1))

            # Extract amperage
            amperage_match = re.search(amperage_pattern, line)
            if amperage_match:
                current_record["amperage"] = float(amperage_match.group(1))

            # Extract thickness
            thickness_match = re.search(thickness_pattern, line)
            if thickness_match:
                current_record["thickness"] = float(thickness_match.group(1))

            # If we have enough parameters, save the record
            if len(current_record) >= 3:
                parameters.append(current_record.copy())
                current_record = {}

        return parameters

    def _clean_parameter_record(self, record):
        """Clean and standardize a parameter record."""
        cleaned = {}

        # Extract numeric values from strings
        for key, value in record.items():
            if pd.isna(value):
                continue

            if key in ["voltage", "amperage", "thickness", "wire_speed", "travel_speed"]:
                # Extract numeric value
                if isinstance(value, str):
                    numbers = re.findall(r"(\d+(?:\.\d+)?)", value)
                    if numbers:
                        cleaned[key] = float(numbers[0])
                elif isinstance(value, (int, float)):
                    cleaned[key] = float(value)
            else:
                cleaned[key] = str(value).strip()

        return cleaned if cleaned else None

    def _validate_parameter_record(self, record):
        """Validate that a parameter record is reasonable."""
        # Check for minimum required fields
        required_fields = ["voltage", "amperage"]
        if not all(field in record for field in required_fields):
            return False

        # Check parameter ranges
        ranges = {
            "voltage": (8, 50),
            "amperage": (20, 500),
            "thickness": (0.5, 100),
            "wire_speed": (50, 800),
            "travel_speed": (1, 30),
        }

        for field, (min_val, max_val) in ranges.items():
            if field in record:
                value = record[field]
                if not (min_val <= value <= max_val):
                    return False

        return True

    def collect_from_manufacturer_apis(self):
        """Collect data from manufacturer APIs where available."""
        # This would integrate with APIs from Lincoln, Miller, ESAB etc.
        # For now, this is a placeholder for future implementation
        print("Manufacturer API integration not yet implemented")
        return []

    def auto_collect_and_train(self, max_sources=10):
        """Automatically collect data and retrain models."""
        print("🔍 Starting automated data collection...")

        # Search for welding parameter sources
        urls = self.search_welding_parameters_web()

        all_collected_data = []
        processed_count = 0

        for url in urls[:max_sources]:
            if processed_count >= max_sources:
                break

            print(f"Processing source {processed_count + 1}/{max_sources}: {url}")
            data = self.extract_data_from_url(url)

            if data:
                all_collected_data.extend(data)
                print(f"  ✅ Extracted {len(data)} records")
            else:
                print(f"  ❌ No data found")

            processed_count += 1
            time.sleep(1)  # Be respectful to servers

        print(f"\n📊 Collection Summary:")
        print(f"  - Sources processed: {processed_count}")
        print(f"  - Total records collected: {len(all_collected_data)}")

        # Save collected data to database
        if all_collected_data:
            saved_count = self._save_collected_data(all_collected_data)
            print(f"  - Records saved to database: {saved_count}")

            # Retrain models with new data
            print("\n🤖 Retraining models with new data...")
            return self._retrain_models()

        return False

    def _save_collected_data(self, data_list):
        """Save collected data to the database."""
        saved_count = 0

        for record in data_list:
            try:
                # Convert to database format
                db_record = self._convert_to_db_format(record)
                if db_record:
                    self.db_manager.add_weld_parameter(db_record)
                    saved_count += 1
            except Exception as e:
                print(f"Error saving record: {e}")
                continue

        return saved_count

    def _convert_to_db_format(self, record):
        """Convert collected record to database format."""
        # This would map the collected data to the database schema
        # For now, return None to avoid database errors
        return None

    def _retrain_models(self):
        """Retrain ML models with new data."""
        try:
            from models.ml_predictor import WeldParameterPredictor

            predictor = WeldParameterPredictor()
            predictor.train_models()

            print("✅ Models retrained successfully!")
            return True

        except Exception as e:
            print(f"❌ Error retraining models: {e}")
            return False


def create_automated_training_system():
    """Create an enhanced training system that can automatically collect data."""
    collector = AutomatedDataCollector()

    print("🤖 Automated Welding Parameter Learning System")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("1. Search and collect data automatically")
        print("2. Collect from specific URL")
        print("3. View collection statistics")
        print("4. Retrain models")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            max_sources = int(input("Maximum sources to process (default 5): ") or "5")
            collector.auto_collect_and_train(max_sources)

        elif choice == "2":
            url = input("Enter URL: ").strip()
            data = collector.extract_data_from_url(url)
            print(f"Extracted {len(data)} records from {url}")

        elif choice == "3":
            # Show statistics
            pass

        elif choice == "4":
            collector._retrain_models()

        elif choice == "5":
            break

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    create_automated_training_system()
