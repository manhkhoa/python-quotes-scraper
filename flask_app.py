#!/usr/bin/env python3
"""
Flask Web Application - Quotes Scraper
Web interface for scraping quotes from quotes.toscrape.com

This Flask app demonstrates:
1. Creating a web server with Python
2. Building REST API endpoints
3. Serving HTML templates
4. Handling HTTP requests and responses
5. Integrating Python backend with JavaScript frontend
"""

# Import Flask components for building web applications
from flask import Flask, render_template, request, jsonify, send_file
# render_template: Renders HTML templates
# request: Handles incoming HTTP requests
# jsonify: Converts Python data to JSON format
# send_file: Sends files to the browser

# Import CORS support to allow web pages to make requests from different domains
from flask_cors import CORS

# Import libraries for web scraping and data processing
import requests          # For making HTTP requests to websites
from bs4 import BeautifulSoup  # For parsing HTML content
import csv              # For creating CSV files
import time             # For adding delays between requests
from datetime import datetime  # For working with dates and times
import io               # For working with in-memory file objects
import os               # For operating system functions

# Create a new Flask application instance
# __name__ is a special Python variable that tells Flask where to look for templates
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing) for all routes
# This allows web pages to make requests to your Flask app from different domains
CORS(app)

class FlaskQuotesScraper:
    """
    A class that handles web scraping specifically for the Flask web application
    
    This class is similar to SimpleQuotesScraper but adapted for web use:
    - Methods return data instead of printing to console
    - Includes additional methods for filtering and statistics
    - Designed to work with Flask API endpoints
    """
    
    def __init__(self):
        """
        Constructor method - initializes the scraper for web use
        
        Sets up:
        - Target website URL
        - Browser headers to avoid being blocked
        - Empty list to store scraped quotes
        """
        # The base URL of the website we want to scrape
        self.base_url = "https://quotes.toscrape.com"
        
        # Headers that make our request look like it's coming from a real browser
        # This helps avoid being blocked by websites that detect automated requests
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
                            'id': len(self.quotes) + len(page_quotes) + 1,  # Unique ID for each quote
                            'text': text,                 # The actual quote text
                            'author': author,             # Who said the quote
                            'tags': tags,                 # List of tags (not joined with semicolons)
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
            
            # Return the quotes from this page
            return page_quotes
            
        except Exception as e:
            # Handle any errors that occur during scraping
            print(f"Error scraping page {page_number}: {e}")
            return []
    
    def scrape_all_pages(self, max_pages=3):
        """
        Scrape quotes from multiple pages
        
        Args:
            max_pages (int): Maximum number of pages to scrape (default: 3)
            
        Returns:
            list: All quotes collected from all pages
        """
        # Reset the quotes list for a fresh scraping session
        self.quotes = []
        
        # Loop through each page number from 1 to max_pages
        for page in range(1, max_pages + 1):
            # Scrape the current page
            page_quotes = self.scrape_page(page)
            
            # If we found quotes on this page, add them to our main quotes list
            if page_quotes:
                # Extend our main quotes list with the quotes from this page
                self.quotes.extend(page_quotes)
            
            # Be respectful to the website - add a delay between requests
            # This prevents overwhelming their server and getting blocked
            if page < max_pages:
                time.sleep(1)  # Wait 1 second before the next request
        
        # Return all collected quotes
        return self.quotes
    
    def get_stats(self):
        """
        Get statistics about the collected quotes
        
        Returns:
            dict: Dictionary containing total quotes, unique authors, and unique tags
        """
        # Check if we have any quotes to get stats for
        if not self.quotes:
            return {
                'total_quotes': 0,
                'unique_authors': 0,
                'unique_tags': 0
            }
        
        # Count unique authors
        # We use a set to automatically remove duplicates
        authors = set(quote['author'] for quote in self.quotes)
        
        # Count unique tags
        all_tags = []
        for quote in self.quotes:
            # Since tags is now a list, we can extend directly
            all_tags.extend(quote['tags'])
        # Convert to set to remove duplicates
        unique_tags = set(all_tags)
        
        # Return statistics as a dictionary
        return {
            'total_quotes': len(self.quotes),
            'unique_authors': len(authors),
            'unique_tags': len(unique_tags)
        }
    
    def filter_quotes(self, search_text='', selected_tag=''):
        """
        Filter quotes based on search text and selected tag
        
        Args:
            search_text (str): Text to search for in quotes and authors
            selected_tag (str): Specific tag to filter by
            
        Returns:
            list: Filtered list of quotes that match the criteria
        """
        # If no filters are applied, return all quotes
        if not search_text and not selected_tag:
            return self.quotes
        
        # Create a list to store filtered quotes
        filtered = []
        
        # Loop through each quote to check if it matches our filters
        for quote in self.quotes:
            # Check if quote text or author contains the search text
            # Convert both to lowercase for case-insensitive search
            matches_search = not search_text or \
                           search_text.lower() in quote['text'].lower() or \
                           search_text.lower() in quote['author'].lower()
            
            # Check if quote has the selected tag
            matches_tag = not selected_tag or selected_tag in quote['tags']
            
            # Only include quotes that match both search and tag filters
            if matches_search and matches_tag:
                filtered.append(quote)
        
        # Return the filtered quotes
        return filtered

# Create a global scraper instance that will be used by all API endpoints
# This means the scraper maintains its state (quotes) between different requests
scraper = FlaskQuotesScraper()

# Flask Route Decorators
# These tell Flask what URL each function should handle

@app.route('/')
def index():
    """
    Main page route - serves the HTML template
    
    When someone visits the root URL (e.g., http://localhost:5000/),
    this function runs and returns the HTML page
    """
    # render_template looks for 'index.html' in the 'templates' folder
    # and returns the rendered HTML to the browser
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """
    API endpoint to handle scraping requests
    
    This endpoint:
    1. Receives a POST request with the number of pages to scrape
    2. Runs the scraper
    3. Returns the results as JSON
    
    Methods: POST (only accepts POST requests, not GET)
    """
    try:
        # Get the JSON data from the request
        # This is the data sent by the JavaScript frontend
        data = request.get_json()
        
        # Get the number of pages to scrape, default to 3 if not specified
        max_pages = data.get('max_pages', 3)
        
        # Start scraping quotes from the website
        quotes = scraper.scrape_all_pages(max_pages)
        
        # Get statistics about the scraped quotes
        stats = scraper.get_stats()
        
        # Return a successful response with the quotes and statistics
        # jsonify converts Python dictionaries to JSON format
        return jsonify({
            'success': True,                    # Indicates the operation was successful
            'quotes': quotes,                   # The actual quote data
            'stats': stats,                     # Statistics about the quotes
            'message': f'Successfully scraped {len(quotes)} quotes'  # Human-readable message
        })
        
    except Exception as e:
        # If any error occurs, return an error response
        # HTTP status code 500 means "Internal Server Error"
        return jsonify({
            'success': False,                   # Indicates the operation failed
            'error': str(e)                     # The error message
        }), 500

@app.route('/api/quotes')
def api_quotes():
    """
    API endpoint to get quotes with optional filtering
    
    This endpoint:
    1. Accepts GET requests with search and tag parameters
    2. Filters quotes based on the parameters
    3. Returns filtered quotes as JSON
    
    Query Parameters:
        search: Text to search for in quotes and authors
        tag: Specific tag to filter by
    """
    # Get query parameters from the URL
    # e.g., /api/quotes?search=love&tag=life
    search_text = request.args.get('search', '')      # Default to empty string if not provided
    selected_tag = request.args.get('tag', '')        # Default to empty string if not provided
    
    # Filter quotes based on the search parameters
    filtered_quotes = scraper.filter_quotes(search_text, selected_tag)
    
    # Return the filtered quotes
    return jsonify({
        'success': True,
        'quotes': filtered_quotes,
        'total': len(filtered_quotes)
    })

@app.route('/api/stats')
def api_stats():
    """
    API endpoint to get statistics about collected quotes
    
    Returns:
        JSON with total quotes, unique authors, and unique tags
    """
    # Get statistics from the scraper
    stats = scraper.get_stats()
    
    # Return the statistics as JSON
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/api/export')
def api_export():
    """
    API endpoint to export quotes to CSV file
    
    This endpoint:
    1. Accepts optional search and tag parameters for filtering
    2. Creates a CSV file in memory
    3. Sends the file to the browser for download
    
    Query Parameters:
        search: Text to search for in quotes and authors
        tag: Specific tag to filter by
    """
    try:
        # Get query parameters for filtering
        search_text = request.args.get('search', '')
        selected_tag = request.args.get('tag', '')
        
        # Filter quotes based on the search parameters
        filtered_quotes = scraper.filter_quotes(search_text, selected_tag)
        
        # Check if we have any quotes to export
        if not filtered_quotes:
            return jsonify({
                'success': False,
                'error': 'No quotes to export'
            }), 400  # HTTP 400 means "Bad Request"
        
        # Create a CSV file in memory (not on disk)
        # This is more efficient for web applications
        output = io.StringIO()
        
        # Create a CSV writer with the appropriate column headers
        writer = csv.DictWriter(output, fieldnames=['id', 'text', 'author', 'tags', 'page', 'timestamp'])
        
        # Write the header row (column names)
        writer.writeheader()
        
        # Write each quote as a row in the CSV file
        for quote in filtered_quotes:
            writer.writerow({
                'id': quote['id'],
                'text': quote['text'],
                'author': quote['author'],
                'tags': '; '.join(quote['tags']),  # Join tags with semicolons for CSV
                'page': quote['page'],
                'timestamp': quote['timestamp']
            })
        
        # Prepare the response
        # seek(0) moves the file pointer to the beginning
        output.seek(0)
        
        # Create a filename with current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quotes_export_{timestamp}.csv"
        
        # Send the CSV file to the browser
        # mimetype='text/csv' tells the browser this is a CSV file
        # as_attachment=True makes the browser download the file instead of displaying it
        # download_name sets the filename for the downloaded file
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),  # Convert string to bytes
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        # If any error occurs, return an error response
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tags')
def api_tags():
    """
    API endpoint to get all available tags
    
    Returns:
        JSON with a list of all unique tags from collected quotes
    """
    # Check if we have any quotes to get tags from
    if not scraper.quotes:
        return jsonify({
            'success': True,
            'tags': []
        })
    
    # Get all tags from all quotes
    all_tags = []
    for quote in scraper.quotes:
        # Since tags is a list, we can extend directly
        all_tags.extend(quote['tags'])
    
    # Remove duplicates and sort alphabetically
    unique_tags = sorted(list(set(all_tags)))
    
    # Return the unique tags as JSON
    return jsonify({
        'success': True,
        'tags': unique_tags
    })

# This is the main entry point when running the Flask app directly
if __name__ == '__main__':
    # Print startup messages
    print("🚀 Starting Flask Quotes Scraper Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/")
    
    # Run the Flask application
    # debug=True enables debug mode (shows detailed error messages)
    # host='0.0.0.0' makes the app accessible from other devices on the network
    # port=5001 sets the port number (5000 is Flask's default, we use 5001 to avoid conflicts)
    app.run(debug=True, host='0.0.0.0', port=5001)
