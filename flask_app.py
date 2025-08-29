#!/usr/bin/env python3
"""
Flask Web Application - Quotes Scraper
Web interface for scraping quotes from quotes.toscrape.com
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
import io
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class FlaskQuotesScraper:
    def __init__(self):
        """Initialize the scraper"""
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
            
            # Make the HTTP request
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
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
                            'id': len(self.quotes) + len(page_quotes) + 1,
                            'text': text,
                            'author': author,
                            'tags': tags,
                            'page': page_number,
                            'timestamp': datetime.now().isoformat()
                        }
                        page_quotes.append(quote_data)
                        
                except Exception as e:
                    print(f"Error parsing quote: {e}")
                    continue
            
            return page_quotes
            
        except Exception as e:
            print(f"Error scraping page {page_number}: {e}")
            return []
    
    def scrape_all_pages(self, max_pages=3):
        """Scrape quotes from multiple pages"""
        self.quotes = []
        
        for page in range(1, max_pages + 1):
            page_quotes = self.scrape_page(page)
            
            if page_quotes:
                self.quotes.extend(page_quotes)
            
            # Be respectful - add delay between requests
            if page < max_pages:
                time.sleep(1)
        
        return self.quotes
    
    def get_stats(self):
        """Get statistics about collected quotes"""
        if not self.quotes:
            return {
                'total_quotes': 0,
                'unique_authors': 0,
                'unique_tags': 0
            }
        
        # Count unique authors
        authors = set(quote['author'] for quote in self.quotes)
        
        # Count unique tags
        all_tags = []
        for quote in self.quotes:
            all_tags.extend(quote['tags'])
        unique_tags = set(all_tags)
        
        return {
            'total_quotes': len(self.quotes),
            'unique_authors': len(authors),
            'unique_tags': len(unique_tags)
        }
    
    def filter_quotes(self, search_text='', selected_tag=''):
        """Filter quotes based on search text and selected tag"""
        if not search_text and not selected_tag:
            return self.quotes
        
        filtered = []
        for quote in self.quotes:
            # Check if quote text contains search text
            matches_search = not search_text or \
                           search_text.lower() in quote['text'].lower() or \
                           search_text.lower() in quote['author'].lower()
            
            # Check if quote has the selected tag
            matches_tag = not selected_tag or selected_tag in quote['tags']
            
            if matches_search and matches_tag:
                filtered.append(quote)
        
        return filtered

# Create global scraper instance
scraper = FlaskQuotesScraper()

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint to scrape quotes"""
    try:
        data = request.get_json()
        max_pages = data.get('max_pages', 3)
        
        # Start scraping
        quotes = scraper.scrape_all_pages(max_pages)
        
        # Get statistics
        stats = scraper.get_stats()
        
        return jsonify({
            'success': True,
            'quotes': quotes,
            'stats': stats,
            'message': f'Successfully scraped {len(quotes)} quotes'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/quotes')
def api_quotes():
    """API endpoint to get all quotes"""
    search_text = request.args.get('search', '')
    selected_tag = request.args.get('tag', '')
    
    # Filter quotes based on search parameters
    filtered_quotes = scraper.filter_quotes(search_text, selected_tag)
    
    return jsonify({
        'success': True,
        'quotes': filtered_quotes,
        'total': len(filtered_quotes)
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint to get statistics"""
    stats = scraper.get_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/api/export')
def api_export():
    """API endpoint to export quotes to CSV"""
    try:
        search_text = request.args.get('search', '')
        selected_tag = request.args.get('tag', '')
        
        # Filter quotes based on search parameters
        filtered_quotes = scraper.filter_quotes(search_text, selected_tag)
        
        if not filtered_quotes:
            return jsonify({
                'success': False,
                'error': 'No quotes to export'
            }), 400
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'text', 'author', 'tags', 'page', 'timestamp'])
        
        # Write header
        writer.writeheader()
        
        # Write data
        for quote in filtered_quotes:
            writer.writerow({
                'id': quote['id'],
                'text': quote['text'],
                'author': quote['author'],
                'tags': '; '.join(quote['tags']),
                'page': quote['page'],
                'timestamp': quote['timestamp']
            })
        
        # Prepare response
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quotes_export_{timestamp}.csv"
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tags')
def api_tags():
    """API endpoint to get all available tags"""
    if not scraper.quotes:
        return jsonify({
            'success': True,
            'tags': []
        })
    
    # Get all unique tags
    all_tags = []
    for quote in scraper.quotes:
        all_tags.extend(quote['tags'])
    unique_tags = sorted(list(set(all_tags)))
    
    return jsonify({
        'success': True,
        'tags': unique_tags
    })

if __name__ == '__main__':
    print("🚀 Starting Flask Quotes Scraper Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
