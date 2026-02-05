# Configuration file for BizBuySell Scraper
# Edit these values to customize your scraper

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE = "credentials.json"
GOOGLE_SHEET_NAME = "BizBuySell NC Listings"

# North Carolina Counties to Scrape
COUNTIES = [
    "iredell",
    "cabarrus",
    "rowan",
    "catawba",
    "gaston",
    "lincoln",
    "mecklenburg"
]

# Scraping Configuration
DELAY_BETWEEN_REQUESTS = 2  # seconds - be respectful to servers
MAX_PAGES_PER_COUNTY = 20   # maximum pages to scrape per county
REQUEST_TIMEOUT = 30         # seconds

# Output Configuration
CSV_BACKUP_FILE = "bizbuysell_listings.csv"
SAVE_CSV_BACKUP = True

# Optional Filters (leave empty for no filtering)
MIN_PRICE = None        # e.g., 50000 for $50,000 minimum
MAX_PRICE = None        # e.g., 500000 for $500,000 maximum
MIN_REVENUE = None      # e.g., 100000 for $100,000 minimum revenue
FRANCHISE_ONLY = False  # True to only collect franchise businesses

# Advanced Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADLESS_BROWSER = True  # For Selenium version - set to False to see browser window
