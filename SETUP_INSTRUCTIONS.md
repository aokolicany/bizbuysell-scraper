# BizBuySell Scraper - Setup Instructions

## Overview
This scraper automatically collects business listings from BizBuySell for specified North Carolina counties and updates a Google Sheet daily.

## Features
- Scrapes 7 NC counties: Iredell, Cabarrus, Rowan, Catawba, Gaston, Lincoln, Mecklenburg
- Extracts: Business type, price, revenue, EBITDA, franchise status, established year, description, and more
- Automatically updates Google Sheets
- Saves CSV backup
- Rate-limited to be respectful to servers

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Sheets API

#### Step 1: Create a Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Name it something like "BizBuySell Scraper"

#### Step 2: Enable Google Sheets API
1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"
4. Also enable "Google Drive API"

#### Step 3: Create Service Account Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: bizbuysell-scraper
   - Description: Service account for scraping BizBuySell
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

#### Step 4: Generate Key File
1. Click on the service account you just created
2. Go to the "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Select "JSON" format
5. Click "Create" - this will download a JSON file
6. Rename this file to `credentials.json`
7. Place it in the same directory as the scraper script

#### Step 5: Share Google Sheet with Service Account
1. Open the downloaded `credentials.json` file
2. Find the "client_email" field (looks like: xxxxx@xxxxx.iam.gserviceaccount.com)
3. Copy this email address
4. Create a new Google Sheet or open an existing one
5. Click "Share" and paste the service account email
6. Give it "Editor" permissions
7. Note the name of your Google Sheet (you'll need this)

### 3. Configure the Scraper

Edit the `bizbuysell_scraper.py` file if needed:

```python
scraper = BizBuySellScraper(
    google_creds_file='credentials.json',  # Path to your credentials
    sheet_name='BizBuySell NC Listings'     # Name of your Google Sheet
)
```

### 4. Run the Scraper

```bash
python bizbuysell_scraper.py
```

The scraper will:
1. Visit BizBuySell for each county
2. Collect all available listings
3. Save data to a CSV file (backup)
4. Update your Google Sheet

## Scheduling Daily Runs

### Option 1: Linux/Mac (using cron)

1. Open crontab editor:
```bash
crontab -e
```

2. Add this line to run daily at 9 AM:
```bash
0 9 * * * cd /path/to/scraper && python bizbuysell_scraper.py >> scraper.log 2>&1
```

### Option 2: Windows (using Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "BizBuySell Daily Scraper"
4. Trigger: Daily at your preferred time
5. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\bizbuysell_scraper.py`
   - Start in: `C:\path\to\scraper\directory`

### Option 3: Cloud-Based (Google Cloud Platform)

1. Upload script to Google Cloud Functions
2. Set up Cloud Scheduler to trigger daily
3. Or use GitHub Actions (see github_actions.yml example below)

## Data Fields Collected

The scraper collects the following information for each listing:

| Field | Description |
|-------|-------------|
| listing_id | Unique listing identifier |
| county | NC County name |
| business_name | Name/title of business |
| business_type | Category/industry |
| price | Asking price |
| revenue | Annual revenue/gross sales |
| ebitda | EBITDA or cash flow |
| franchise | Yes/No franchise status |
| established_year | Year business was established |
| location | City/location details |
| employees | Number of employees |
| description | Full business description |
| facilities | Real estate/facility information |
| reason_for_selling | Why owner is selling |
| url | Link to listing |
| scrape_date | When data was collected |

## Troubleshooting

### "No listings found"
- BizBuySell may have changed their website structure
- Check if the county URLs are correct
- Website might be blocking automated access (add delays)

### Google Sheets Authentication Error
- Verify credentials.json is in the correct location
- Check that the service account email has access to the sheet
- Ensure both Google Sheets API and Drive API are enabled

### Rate Limiting / Blocked
- The scraper includes 2-second delays between requests
- If blocked, increase the delay time in `time.sleep(2)`
- Consider using proxy rotation (advanced)

### Missing Data Fields
- BizBuySell may not show all fields for every listing
- Some listings have incomplete information
- The scraper handles missing fields gracefully

## Customization

### Change Counties
Edit the `counties` list in the `__init__` method:

```python
self.counties = [
    'iredell', 'cabarrus', 'rowan', 'catawba', 
    'gaston', 'lincoln', 'mecklenburg', 'union'  # Add more
]
```

### Add More States
Modify the `build_search_url` method to accept different states.

### Filter by Price Range
Add filtering logic in the `scrape_search_results` method.

## Legal Considerations

- **Respect robots.txt**: BizBuySell's robots.txt should be reviewed
- **Terms of Service**: Review BizBuySell's ToS for scraping policies
- **Rate Limiting**: The script includes delays to avoid overwhelming servers
- **Personal Use**: This is intended for personal research, not commercial redistribution
- **Data Privacy**: Don't share scraped data publicly without permission

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console output
3. Check the CSV backup file to see what data was collected
4. Verify Google Sheets permissions and API access

## Files Generated

- `bizbuysell_listings.csv` - Backup CSV file with all data
- `scraper.log` - Log file (if using cron scheduling)
- Google Sheet - Live updated spreadsheet

## Updates and Maintenance

BizBuySell may update their website structure. If the scraper stops working:
1. Inspect the BizBuySell website HTML
2. Update CSS selectors and parsing logic
3. Test on a single county first
4. Check for any anti-scraping measures

---

**Note**: Web scraping should be done responsibly and ethically. Always respect website terms of service and rate limits.
