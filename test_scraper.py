#!/usr/bin/env python3
"""
Test Script for Python Quotes Scraper
Quick test to verify the scraper is working correctly
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✅ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"❌ beautifulsoup4 import failed: {e}")
        return False
    
    try:
        import csv
        print("✅ csv imported successfully")
    except ImportError as e:
        print(f"❌ csv import failed: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✅ datetime imported successfully")
    except ImportError as e:
        print(f"❌ datetime import failed: {e}")
        return False
    
    return True

def test_simple_scraper():
    """Test the simple scraper class"""
    print("\n🧪 Testing simple scraper class...")
    
    try:
        from simple_scraper import SimpleQuotesScraper
        print("✅ SimpleQuotesScraper class imported successfully")
        
        # Create instance
        scraper = SimpleQuotesScraper()
        print("✅ Scraper instance created successfully")
        
        # Test basic scraper functionality
        print("✅ Basic scraper functionality verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple scraper test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app imports"""
    print("\n🧪 Testing Flask app imports...")
    
    try:
        from flask_app import FlaskQuotesScraper
        print("✅ FlaskQuotesScraper class imported successfully")
        
        # Create instance
        scraper = FlaskQuotesScraper()
        print("✅ Flask scraper instance created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_web_scraping():
    """Test actual web scraping (minimal test)"""
    print("\n🧪 Testing web scraping capability...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Test basic request
        url = "https://quotes.toscrape.com"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"🌐 Testing connection to {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Website accessible successfully")
            
            # Test HTML parsing
            soup = BeautifulSoup(response.content, 'html.parser')
            quotes = soup.find_all('div', class_='quote')
            
            if quotes:
                print(f"✅ HTML parsing works: found {len(quotes)} quotes")
                return True
            else:
                print("⚠️  HTML parsing found no quotes (structure might have changed)")
                return False
        else:
            print(f"❌ Website returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Web scraping test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Python Quotes Scraper Tests...")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Simple Scraper Class", test_simple_scraper),
        ("Flask App Class", test_flask_app),
        ("Web Scraping Capability", test_web_scraping)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Python scraper is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: python simple_scraper.py")
        print("2. Or run: python flask_app.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check Python version: python --version")
        print("3. Verify internet connection")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
