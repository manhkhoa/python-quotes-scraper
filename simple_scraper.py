#!/usr/bin/env python3
"""
Simple Quotes Scraper - Python Version
Scrapes quotes from quotes.toscrape.com and exports to CSV

This script demonstrates basic web scraping concepts:
1. Making HTTP requests to websites
2. Parsing HTML content to extract data
3. Storing data in structured format
4. Exporting data to CSV files
"""

# Import required libraries
import requests          # For making HTTP requests to websites
from bs4 import BeautifulSoup  # For parsing HTML content
import csv              # For creating and writing CSV files
import time             # For adding delays between requests
from datetime import datetime  # For working with dates and times
import sys              # For accessing command-line arguments

class SimpleQuotesScraper:
    """
    A class that handles web scraping of quotes from quotes.toscrape.com
    
    This class demonstrates object-oriented programming concepts:
    - Constructor method (__init__)
    - Instance methods for different functionalities
    - Error handling with try-catch blocks
    - Data processing and storage
    """
    
    def __init__(self):
        """
        Constructor method - runs when creating a new scraper instance
        
        This method initializes the scraper with:
        - The target website URL
        - Browser headers to avoid being blocked
        - An empty list to store scraped quotes
        """
        # The base URL of the website we want to scrape
        self.base_url = "https://quotes.toscrape.com"
        
        # Headers that make our request look like it's coming from a real browser
        # Some websites block automated requests, so this helps avoid detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize an empty list to store all the quotes we scrape
        self.quotes = []
        
    def scrape_page(self, page_number):
        """
        Scrape quotes from a specific page number
        
        Args:
            page_number (int): The page number to scrape (1, 2, 3, etc.)
            
        Returns:
            list: A list of dictionaries containing quote data from this page
        """
        try:
            # Construct the URL for the specific page
            # Page 1 is just the base URL, other pages have /page/X/ added
            if page_number == 1:
                url = self.base_url
            else:
                url = f"{self.base_url}/page/{page_number}/"
            
            # Print a message showing which page we're currently scraping
            print(f"Scraping page {page_number}: {url}")
            
            # Make an HTTP GET request to the website
            # This is like visiting the webpage in your browser
            response = requests.get(url, headers=self.headers)
            
            # Check if the request was successful (status code 200)
            # If not, this will raise an exception
            response.raise_for_status()
            
            # Parse the HTML content of the webpage
            # BeautifulSoup makes it easy to extract information from HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all HTML elements that contain quotes
            # We're looking for <div> elements with class="quote"
            quote_elements = soup.find_all('div', class_='quote')
            
            # Create a list to store quotes from this specific page
            page_quotes = []
            
            # Loop through each quote element found on the page
            for quote_element in quote_elements:
                try:
                    # Extract the quote text
                    # Look for a <span> element with class="text" inside the quote div
                    text_element = quote_element.find('span', class_='text')
                    # Get the text content and remove extra whitespace
                    text = text_element.get_text(strip=True) if text_element else ''
                    
                    # Extract the author name
                    # Look for a <small> element with class="author"
                    author_element = quote_element.find('small', class_='author')
                    author = author_element.get_text(strip=True) if author_element else ''
                    
                    # Extract all the tags
                    # Look for all <a> elements with class="tag"
                    tag_elements = quote_element.find_all('a', class_='tag')
                    # Convert each tag to text and store in a list
                    tags = [tag.get_text(strip=True) for tag in tag_elements]
                    
                    # Only add quotes that have both text and author
                    # This prevents empty or incomplete quotes from being added
                    if text and author:
                        # Create a dictionary with all the quote information
                        quote_data = {
                            'id': len(self.quotes) + 1,  # Give each quote a unique ID
                            'text': text,                 # The actual quote text
                            'author': author,             # Who said the quote
                            'tags': '; '.join(tags),      # Join tags with semicolons
                            'page': page_number,          # Which page this quote came from
                            'timestamp': datetime.now().isoformat()  # When we scraped it
                        }
                        # Add this quote to our page quotes list
                        page_quotes.append(quote_data)
                        
                except Exception as e:
                    # If there's an error parsing a specific quote, print the error
                    # and continue with the next quote instead of crashing
                    print(f"Error parsing quote: {e}")
                    continue
            
            # Print how many quotes we found on this page
            print(f"Found {len(page_quotes)} quotes on page {page_number}")
            
            # Return the quotes from this page
            return page_quotes
            
        except requests.RequestException as e:
            # Handle errors related to HTTP requests (network issues, bad URLs, etc.)
            print(f"Error scraping page {page_number}: {e}")
            return []
        except Exception as e:
            # Handle any other unexpected errors
            print(f"Unexpected error on page {page_number}: {e}")
            return []
    
    def scrape_all_pages(self, max_pages=5):
        """
        Scrape quotes from multiple pages
        
        Args:
            max_pages (int): Maximum number of pages to scrape (default: 5)
        """
        print(f"Starting to scrape up to {max_pages} pages...")
        
        # Loop through each page number from 1 to max_pages
        for page in range(1, max_pages + 1):
            # Scrape the current page
            page_quotes = self.scrape_page(page)
            
            # If we found quotes on this page, add them to our main quotes list
            if page_quotes:
                # Extend our main quotes list with the quotes from this page
                self.quotes.extend(page_quotes)
                # Print progress update
                print(f"Total quotes collected so far: {len(self.quotes)}")
            else:
                # If no quotes were found, stop scraping
                # This might happen if we've reached the last page
                print(f"No quotes found on page {page}, stopping...")
                break
            
            # Be respectful to the website - add a delay between requests
            # This prevents overwhelming their server and getting blocked
            if page < max_pages:
                time.sleep(1)  # Wait 1 second before the next request
        
        # Print final summary
        print(f"\nScraping completed! Total quotes collected: {len(self.quotes)}")
    
    def export_to_csv(self, filename=None):
        """
        Export all scraped quotes to a CSV file
        
        Args:
            filename (str, optional): Name of the CSV file. If not provided,
                                    a filename with timestamp will be generated.
        """
        # Check if we have any quotes to export
        if not self.quotes:
            print("No quotes to export!")
            return
        
        # If no filename was provided, create one with current timestamp
        if filename is None:
            # Create timestamp in format: YYYYMMDD_HHMMSS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quotes_export_{timestamp}.csv"
        
        try:
            # Open a file for writing
            # 'w' means write mode (overwrites existing file)
            # newline='' prevents extra blank lines in CSV
            # encoding='utf-8' ensures proper handling of special characters
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Define the column headers for our CSV file
                fieldnames = ['id', 'text', 'author', 'tags', 'page', 'timestamp']
                
                # Create a CSV writer that can handle dictionaries
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write the header row (column names)
                writer.writeheader()
                
                # Write each quote as a row in the CSV file
                for quote in self.quotes:
                    writer.writerow(quote)
            
            # Print success message
            print(f"Successfully exported {len(self.quotes)} quotes to {filename}")
            
        except Exception as e:
            # Handle any errors that occur during file writing
            print(f"Error exporting to CSV: {e}")
    
    def display_stats(self):
        """
        Display statistics about the collected quotes
        
        This method shows:
        - Total number of quotes
        - Number of unique authors
        - Number of unique tags
        - Sample quotes
        """
        # Check if we have any quotes to display stats for
        if not self.quotes:
            print("No quotes collected yet.")
            return
        
        # Print a nice header for the statistics
        print("\n" + "="*50)
        print("QUOTES SCRAPER STATISTICS")
        print("="*50)
        print(f"Total Quotes: {len(self.quotes)}")
        
        # Count unique authors
        # We use a set to automatically remove duplicates
        authors = set(quote['author'] for quote in self.quotes)
        print(f"Unique Authors: {len(authors)}")
        
        # Count unique tags
        all_tags = []
        for quote in self.quotes:
            if quote['tags']:
                # Split tags by semicolon and add to our list
                all_tags.extend(quote['tags'].split('; '))
        # Convert to set to remove duplicates
        unique_tags = set(all_tags)
        print(f"Unique Tags: {len(unique_tags)}")
        
        # Show a few sample quotes
        print(f"\nSample Quotes:")
        # Loop through first 3 quotes (or fewer if we have less than 3)
        for i, quote in enumerate(self.quotes[:3], 1):
            # Show first 80 characters of quote text, then add "..."
            print(f"{i}. \"{quote['text'][:80]}...\" - {quote['author']}")
        
        print("="*50)
    
    def run(self, max_pages=5):
        """
        Main method to run the complete scraping process
        
        This method orchestrates the entire workflow:
        1. Scrape quotes from multiple pages
        2. Display statistics
        3. Export to CSV
        
        Args:
            max_pages (int): Maximum number of pages to scrape
        """
        print("🚀 Starting Python Quotes Scraper...")
        print("="*50)
        
        # Step 1: Scrape quotes from the website
        self.scrape_all_pages(max_pages)
        
        # Step 2: Show statistics about what we collected
        self.display_stats()
        
        # Step 3: Export the quotes to a CSV file
        if self.quotes:
            self.export_to_csv()
        
        print("\n✅ Scraping process completed!")

def main():
    """
    Main function - this is the entry point of the script
    
    This function:
    1. Creates a scraper instance
    2. Gets the number of pages from command line arguments
    3. Runs the scraper
    """
    # Create a new instance of our scraper class
    scraper = SimpleQuotesScraper()
    
    # Get the number of pages to scrape from command line arguments
    # Default to 3 pages if no argument is provided
    max_pages = 3
    if len(sys.argv) > 1:
        try:
            # Convert the command line argument to an integer
            max_pages = int(sys.argv[1])
        except ValueError:
            # If the argument isn't a valid number, use the default
            print("Invalid page number. Using default: 3 pages")
    
    # Run the scraper with the specified number of pages
    scraper.run(max_pages)

# This is a special Python construct that only runs the main function
# if this script is run directly (not imported as a module)
if __name__ == "__main__":
    main()
