#!/usr/bin/env python3
"""
Simple Quotes Scraper - Python Version
Scrapes quotes from quotes.toscrape.com and exports to CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import sys

class SimpleQuotesScraper:
    def __init__(self):
        """Initialize the scraper with base URL and headers"""
        self.base_url = "https://quotes.toscrape.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.quotes = []
        
    def scrape_page(self, page_number):
        """Scrape quotes from a specific page"""
        try:
            # Construct the URL for the page
            if page_number == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}/page/{page_number}/"
            
            print(f"Scraping page {page_number}: {url}")
            
            # Make the HTTP request
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all quote containers
            quote_elements = soup.find_all('div', class_='quote')
            
            page_quotes = []
            for quote_element in quote_elements:
                try:
                    # Extract quote text
                    text_element = quote_element.find('span', class_='text')
                    text = text_element.get_text(strip=True) if text_element else ''
                    
                    # Extract author name
                    author_element = quote_element.find('small', class_='author')
                    author = author_element.get_text(strip=True) if author_element else ''
                    
                    # Extract tags
                    tag_elements = quote_element.find_all('a', class_='tag')
                    tags = [tag.get_text(strip=True) for tag in tag_elements]
                    
                    # Only add quotes with both text and author
                    if text and author:
                        quote_data = {
                            'id': len(self.quotes) + 1,
                            'text': text,
                            'author': author,
                            'tags': '; '.join(tags),
                            'page': page_number,
                            'timestamp': datetime.now().isoformat()
                        }
                        page_quotes.append(quote_data)
                        
                except Exception as e:
                    print(f"Error parsing quote: {e}")
                    continue
            
            print(f"Found {len(page_quotes)} quotes on page {page_number}")
            return page_quotes
            
        except requests.RequestException as e:
            print(f"Error scraping page {page_number}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error on page {page_number}: {e}")
            return []
    
    def scrape_all_pages(self, max_pages=5):
        """Scrape quotes from multiple pages"""
        print(f"Starting to scrape up to {max_pages} pages...")
        
        for page in range(1, max_pages + 1):
            page_quotes = self.scrape_page(page)
            
            if page_quotes:
                self.quotes.extend(page_quotes)
                print(f"Total quotes collected so far: {len(self.quotes)}")
            else:
                print(f"No quotes found on page {page}, stopping...")
                break
            
            # Be respectful - add delay between requests
            if page < max_pages:
                time.sleep(1)
        
        print(f"\nScraping completed! Total quotes collected: {len(self.quotes)}")
    
    def export_to_csv(self, filename=None):
        """Export quotes to CSV file"""
        if not self.quotes:
            print("No quotes to export!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quotes_export_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = ['id', 'text', 'author', 'tags', 'page', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header row
                writer.writeheader()
                
                # Write quote data
                for quote in self.quotes:
                    writer.writerow(quote)
            
            print(f"Successfully exported {len(self.quotes)} quotes to {filename}")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def display_stats(self):
        """Display statistics about collected quotes"""
        if not self.quotes:
            print("No quotes collected yet.")
            return
        
        print("\n" + "="*50)
        print("QUOTES SCRAPER STATISTICS")
        print("="*50)
        print(f"Total Quotes: {len(self.quotes)}")
        
        # Count unique authors
        authors = set(quote['author'] for quote in self.quotes)
        print(f"Unique Authors: {len(authors)}")
        
        # Count unique tags
        all_tags = []
        for quote in self.quotes:
            if quote['tags']:
                all_tags.extend(quote['tags'].split('; '))
        unique_tags = set(all_tags)
        print(f"Unique Tags: {len(unique_tags)}")
        
        # Show sample quotes
        print(f"\nSample Quotes:")
        for i, quote in enumerate(self.quotes[:3], 1):
            print(f"{i}. \"{quote['text'][:80]}...\" - {quote['author']}")
        
        print("="*50)
    
    def run(self, max_pages=5):
        """Main method to run the scraper"""
        print("🚀 Starting Python Quotes Scraper...")
        print("="*50)
        
        # Scrape quotes
        self.scrape_all_pages(max_pages)
        
        # Display statistics
        self.display_stats()
        
        # Export to CSV
        if self.quotes:
            self.export_to_csv()
        
        print("\n✅ Scraping process completed!")

def main():
    """Main function to run the scraper"""
    # Create scraper instance
    scraper = SimpleQuotesScraper()
    
    # Get number of pages from command line argument, default to 3
    max_pages = 3
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            print("Invalid page number. Using default: 3 pages")
    
    # Run the scraper
    scraper.run(max_pages)

if __name__ == "__main__":
    main()
