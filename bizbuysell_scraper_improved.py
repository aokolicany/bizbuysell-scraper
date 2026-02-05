"""
Improved BizBuySell Scraper with Better Anti-Detection
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import random


class ImprovedBizBuySellScraper:
    def __init__(self, google_creds_file='credentials.json', sheet_name='BizBuySell NC Listings'):
        self.base_url = "https://www.bizbuysell.com"
        self.counties = [
            'iredell', 'cabarrus', 'rowan', 'catawba', 
            'gaston', 'lincoln', 'mecklenburg'
        ]
        self.google_creds_file = google_creds_file
        self.sheet_name = sheet_name
        
        # Rotating user agents to appear more human
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Create a session to persist cookies
        self.session = requests.Session()
        
    def get_headers(self):
        """Get realistic headers with rotating user agent"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
    
    def build_search_url(self, county, state='north-carolina'):
        """Build search URL - try different URL formats"""
        # BizBuySell uses various URL patterns
        return f"{self.base_url}/businesses-for-sale/{state}/{county}-county/"
    
    def scrape_with_retry(self, url, max_retries=3):
        """Try to fetch URL with retries and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Random delay between 3-7 seconds to appear more human
                delay = random.uniform(3, 7)
                print(f"  Waiting {delay:.1f} seconds...")
                time.sleep(delay)
                
                response = self.session.get(
                    url, 
                    headers=self.get_headers(),
                    timeout=30,
                    allow_redirects=True
                )
                
                # Check if we got a valid response
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"  Got 403 Forbidden on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        wait_time = (2 ** attempt) * 5
                        print(f"  Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                else:
                    print(f"  Got status code {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"  Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)
        
        return None
    
    def scrape_search_results(self, county):
        """Scrape listings from county - simplified approach"""
        search_url = self.build_search_url(county)
        all_listings = []
        
        print(f"\nScraping {county.title()} County...")
        print(f"URL: {search_url}")
        
        # Try to get the search page
        response = self.scrape_with_retry(search_url)
        
        if not response:
            print(f"  Could not access {county} county page")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for listing cards/links - BizBuySell uses various class names
        # We'll try multiple selectors
        listing_elements = (
            soup.find_all('a', href=re.compile(r'/businesses-for-sale/')) or
            soup.find_all('div', class_=re.compile(r'listing|business-card', re.I)) or
            soup.find_all('article')
        )
        
        print(f"  Found {len(listing_elements)} potential listings")
        
        # Extract basic info from search results page
        for elem in listing_elements[:10]:  # Limit to first 10 to be respectful
            try:
                listing_data = {
                    'county': county.title(),
                    'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Try to extract title/business name
                title_elem = (
                    elem.find('h2') or elem.find('h3') or 
                    elem.find('a', class_=re.compile(r'title|name', re.I)) or
                    elem.find('span', class_=re.compile(r'title|name', re.I))
                )
                if title_elem:
                    listing_data['business_name'] = title_elem.get_text(strip=True)
                
                # Try to extract price
                price_elem = (
                    elem.find(class_=re.compile(r'price', re.I)) or
                    elem.find(text=re.compile(r'\$[\d,]+'))
                )
                if price_elem:
                    if hasattr(price_elem, 'get_text'):
                        listing_data['price'] = price_elem.get_text(strip=True)
                    else:
                        listing_data['price'] = str(price_elem).strip()
                
                # Try to extract location
                location_elem = elem.find(class_=re.compile(r'location|city', re.I))
                if location_elem:
                    listing_data['location'] = location_elem.get_text(strip=True)
                
                # Try to find the listing URL
                link = elem.find('a', href=re.compile(r'/businesses-for-sale/'))
                if link and link.get('href'):
                    href = link['href']
                    listing_data['url'] = href if href.startswith('http') else self.base_url + href
                
                if listing_data.get('business_name') or listing_data.get('price'):
                    all_listings.append(listing_data)
                    
            except Exception as e:
                print(f"  Error parsing listing: {str(e)}")
                continue
        
        print(f"  Collected {len(all_listings)} listings from {county.title()}")
        return all_listings
    
    def scrape_all_counties(self):
        """Scrape all counties"""
        all_listings = []
        
        # Visit homepage first to get cookies
        print("Initializing session...")
        try:
            self.session.get(self.base_url, headers=self.get_headers(), timeout=10)
            time.sleep(2)
        except:
            print("Could not access homepage, continuing anyway...")
        
        for county in self.counties:
            county_listings = self.scrape_search_results(county)
            all_listings.extend(county_listings)
            
            # Longer delay between counties
            if county != self.counties[-1]:
                delay = random.uniform(5, 10)
                print(f"\nWaiting {delay:.1f} seconds before next county...")
                time.sleep(delay)
        
        print(f"\nTotal listings collected: {len(all_listings)}")
        return all_listings
    
    def update_google_sheet(self, listings_data):
        """Update Google Sheet with data"""
        if not listings_data:
            print("No data to update in Google Sheet")
            return False
            
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.google_creds_file, scope)
            client = gspread.authorize(creds)
            
            try:
                sheet = client.open(self.sheet_name).sheet1
            except:
                spreadsheet = client.create(self.sheet_name)
                spreadsheet.share('', perm_type='anyone', role='reader')
                sheet = spreadsheet.sheet1
            
            df = pd.DataFrame(listings_data)
            
            columns = [
                'county', 'business_name', 'price', 'location', 
                'url', 'scrape_date'
            ]
            
            for col in columns:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[columns]
            
            sheet.clear()
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            print(f"\nSuccessfully updated Google Sheet: {self.sheet_name}")
            print(f"Total rows: {len(df) + 1}")
            return True
            
        except Exception as e:
            print(f"Error updating Google Sheet: {str(e)}")
            return False
    
    def save_to_csv(self, listings_data, filename='bizbuysell_listings.csv'):
        """Save to CSV"""
        if not listings_data:
            print("No data to save to CSV")
            return
            
        df = pd.DataFrame(listings_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    def run(self):
        """Main execution"""
        print("=" * 60)
        print("Improved BizBuySell Scraper - North Carolina Counties")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        listings = self.scrape_all_counties()
        
        if not listings:
            print("\nNo listings found!")
            print("This could mean:")
            print("1. BizBuySell is still blocking automated access")
            print("2. There are no active listings in these counties")
            print("3. The website structure has changed significantly")
            return
        
        self.save_to_csv(listings)
        self.update_google_sheet(listings)
        
        print("=" * 60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


if __name__ == "__main__":
    scraper = ImprovedBizBuySellScraper(
        google_creds_file='credentials.json',
        sheet_name='BizBuySell NC Listings'
    )
    scraper.run()
