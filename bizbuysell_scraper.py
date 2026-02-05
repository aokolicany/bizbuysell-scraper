"""
BizBuySell Daily Scraper for North Carolina Counties
Scrapes business listings and updates Google Sheets
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


class BizBuySellScraper:
    def __init__(self, google_creds_file='credentials.json', sheet_name='BizBuySell Listings'):
        """
        Initialize the scraper
        
        Args:
            google_creds_file: Path to Google service account credentials JSON
            sheet_name: Name of the Google Sheet to update
        """
        self.base_url = "https://www.bizbuysell.com"
        self.counties = [
            'iredell', 'cabarrus', 'rowan', 'catawba', 
            'gaston', 'lincoln', 'mecklenburg'
        ]
        self.google_creds_file = google_creds_file
        self.sheet_name = sheet_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
    def build_search_url(self, county, state='NC'):
        """Build search URL for a specific county"""
        # BizBuySell URL structure for location-based searches
        return f"{self.base_url}/businesses-for-sale/in/{state}/{county}-county/"
    
    def scrape_listing_page(self, url):
        """Scrape a single listing detail page"""
        try:
            time.sleep(2)  # Be polite to the server
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            listing_data = {
                'url': url,
                'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Extract business type/category
            category = soup.find('div', class_='category') or soup.find('span', class_='category')
            listing_data['business_type'] = category.text.strip() if category else ''
            
            # Extract price
            price_elem = soup.find('span', class_='price') or soup.find('div', class_='price')
            if price_elem:
                price_text = price_elem.text.strip()
                listing_data['price'] = price_text
            else:
                listing_data['price'] = ''
            
            # Extract revenue
            revenue_label = soup.find(text=re.compile(r'Revenue|Gross Sales', re.I))
            if revenue_label:
                revenue_elem = revenue_label.find_parent().find_next_sibling()
                listing_data['revenue'] = revenue_elem.text.strip() if revenue_elem else ''
            else:
                listing_data['revenue'] = ''
            
            # Extract EBITDA / Cash Flow
            ebitda_label = soup.find(text=re.compile(r'EBITDA|Cash Flow|Net Income', re.I))
            if ebitda_label:
                ebitda_elem = ebitda_label.find_parent().find_next_sibling()
                listing_data['ebitda'] = ebitda_elem.text.strip() if ebitda_elem else ''
            else:
                listing_data['ebitda'] = ''
            
            # Extract franchise status
            franchise_label = soup.find(text=re.compile(r'Franchise', re.I))
            if franchise_label:
                franchise_elem = franchise_label.find_parent().find_next_sibling()
                franchise_text = franchise_elem.text.strip() if franchise_elem else ''
                listing_data['franchise'] = 'Yes' if 'yes' in franchise_text.lower() else 'No'
            else:
                listing_data['franchise'] = 'No'
            
            # Extract established year
            established_label = soup.find(text=re.compile(r'Established|Year Established', re.I))
            if established_label:
                established_elem = established_label.find_parent().find_next_sibling()
                listing_data['established_year'] = established_elem.text.strip() if established_elem else ''
            else:
                listing_data['established_year'] = ''
            
            # Extract business description
            description = soup.find('div', class_='description') or soup.find('div', id='description')
            listing_data['description'] = description.text.strip() if description else ''
            
            # Extract business name/title
            title = soup.find('h1') or soup.find('title')
            listing_data['business_name'] = title.text.strip() if title else ''
            
            # Extract location details
            location = soup.find('span', class_='location') or soup.find('div', class_='location')
            listing_data['location'] = location.text.strip() if location else ''
            
            # Extract employees count
            employees_label = soup.find(text=re.compile(r'Employees', re.I))
            if employees_label:
                employees_elem = employees_label.find_parent().find_next_sibling()
                listing_data['employees'] = employees_elem.text.strip() if employees_elem else ''
            else:
                listing_data['employees'] = ''
            
            # Extract facilities info
            facilities_label = soup.find(text=re.compile(r'Facilities|Real Estate', re.I))
            if facilities_label:
                facilities_elem = facilities_label.find_parent().find_next_sibling()
                listing_data['facilities'] = facilities_elem.text.strip() if facilities_elem else ''
            else:
                listing_data['facilities'] = ''
            
            # Extract reason for selling
            reason_label = soup.find(text=re.compile(r'Reason for Selling', re.I))
            if reason_label:
                reason_elem = reason_label.find_parent().find_next_sibling()
                listing_data['reason_for_selling'] = reason_elem.text.strip() if reason_elem else ''
            else:
                listing_data['reason_for_selling'] = ''
            
            # Extract listing ID
            listing_id_match = re.search(r'/listing/(\d+)', url)
            listing_data['listing_id'] = listing_id_match.group(1) if listing_id_match else ''
            
            return listing_data
            
        except Exception as e:
            print(f"Error scraping listing {url}: {str(e)}")
            return None
    
    def scrape_search_results(self, county):
        """Scrape all listings from a county search page"""
        search_url = self.build_search_url(county)
        all_listings = []
        page = 1
        
        print(f"Scraping {county.title()} County...")
        
        while True:
            try:
                # Build paginated URL
                if page > 1:
                    paginated_url = f"{search_url}?page={page}"
                else:
                    paginated_url = search_url
                
                print(f"  Fetching page {page}...")
                time.sleep(2)  # Rate limiting
                
                response = requests.get(paginated_url, headers=self.headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all listing links
                listing_links = soup.find_all('a', href=re.compile(r'/listing/'))
                
                if not listing_links:
                    print(f"  No more listings found on page {page}")
                    break
                
                # Get unique listing URLs
                listing_urls = set()
                for link in listing_links:
                    href = link.get('href')
                    if href and '/listing/' in href:
                        full_url = href if href.startswith('http') else self.base_url + href
                        listing_urls.add(full_url)
                
                print(f"  Found {len(listing_urls)} unique listings on page {page}")
                
                # Scrape each listing
                for listing_url in listing_urls:
                    listing_data = self.scrape_listing_page(listing_url)
                    if listing_data:
                        listing_data['county'] = county.title()
                        all_listings.append(listing_data)
                
                # Check for next page
                next_button = soup.find('a', text=re.compile(r'Next|›'))
                if not next_button or page >= 20:  # Safety limit
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error scraping search results for {county}: {str(e)}")
                break
        
        return all_listings
    
    def scrape_all_counties(self):
        """Scrape listings from all specified counties"""
        all_listings = []
        
        for county in self.counties:
            county_listings = self.scrape_search_results(county)
            all_listings.extend(county_listings)
            print(f"Collected {len(county_listings)} listings from {county.title()} County")
        
        print(f"\nTotal listings collected: {len(all_listings)}")
        return all_listings
    
    def update_google_sheet(self, listings_data):
        """Update Google Sheet with scraped data"""
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            
            # Authenticate
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.google_creds_file, scope)
            client = gspread.authorize(creds)
            
            # Open the sheet
            try:
                sheet = client.open(self.sheet_name).sheet1
            except:
                # Create new spreadsheet if it doesn't exist
                spreadsheet = client.create(self.sheet_name)
                spreadsheet.share('', perm_type='anyone', role='reader')
                sheet = spreadsheet.sheet1
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(listings_data)
            
            # Define column order
            columns = [
                'listing_id', 'county', 'business_name', 'business_type', 
                'price', 'revenue', 'ebitda', 'franchise', 'established_year',
                'location', 'employees', 'description', 'facilities', 
                'reason_for_selling', 'url', 'scrape_date'
            ]
            
            # Reorder columns (add missing ones with empty values)
            for col in columns:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[columns]
            
            # Clear existing data
            sheet.clear()
            
            # Update with new data
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
            
            print(f"\nSuccessfully updated Google Sheet: {self.sheet_name}")
            print(f"Total rows: {len(df) + 1}")  # +1 for header
            
            return True
            
        except Exception as e:
            print(f"Error updating Google Sheet: {str(e)}")
            return False
    
    def save_to_csv(self, listings_data, filename='bizbuysell_listings.csv'):
        """Save listings to CSV as backup"""
        df = pd.DataFrame(listings_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("BizBuySell Scraper - North Carolina Counties")
        print("=" * 60)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Counties: {', '.join([c.title() for c in self.counties])}")
        print("=" * 60)
        
        # Scrape all listings
        listings = self.scrape_all_counties()
        
        if not listings:
            print("\nNo listings found!")
            return
        
        # Save to CSV backup
        self.save_to_csv(listings)
        
        # Update Google Sheet
        self.update_google_sheet(listings)
        
        print("=" * 60)
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


if __name__ == "__main__":
    # Initialize and run scraper
    scraper = BizBuySellScraper(
        google_creds_file='credentials.json',
        sheet_name='BizBuySell NC Listings'
    )
    scraper.run()
