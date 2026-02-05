# BizBuySell NC Counties Scraper

Automated daily scraper for business listings in 7 North Carolina counties: Iredell, Cabarrus, Rowan, Catawba, Gaston, Lincoln, and Mecklenburg.

## What This Does

- 🔍 Scrapes BizBuySell for business listings in your specified counties
- 📊 Extracts: business type, price, revenue, EBITDA, franchise status, established year, full descriptions, and more
- 📈 Automatically updates a Google Sheet with all data
- 💾 Saves a CSV backup file
- ⏰ Can be scheduled to run daily automatically

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Sheets Access

1. **Create a Google Cloud Project**: https://console.cloud.google.com/
2. **Enable APIs**: Enable "Google Sheets API" and "Google Drive API"
3. **Create Service Account**: Create credentials and download as `credentials.json`
4. **Share Your Sheet**: Share your Google Sheet with the service account email

**Detailed instructions**: See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)

### 3. Test Your Setup

```bash
python test_setup.py
```

### 4. Run the Scraper

```bash
python bizbuysell_scraper.py
```

## Files Included

| File | Purpose |
|------|---------|
| `bizbuysell_scraper.py` | Main scraper (uses requests + BeautifulSoup) |
| `bizbuysell_scraper_selenium.py` | Alternative scraper (uses Selenium for JavaScript-heavy pages) |
| `test_setup.py` | Verify your setup before running |
| `requirements.txt` | Python package dependencies |
| `SETUP_INSTRUCTIONS.md` | Detailed setup guide |
| `github_actions_workflow.yml` | Cloud automation setup (optional) |

## Data Collected

For each business listing:

- Listing ID
- County
- Business Name
- Business Type/Category
- Asking Price
- Annual Revenue
- EBITDA/Cash Flow
- Franchise (Yes/No)
- Year Established
- Location Details
- Number of Employees
- Full Description
- Facility Information
- Reason for Selling
- Listing URL
- Date Scraped

## Scheduling Daily Runs

### Option 1: cron (Linux/Mac)

```bash
crontab -e
```

Add: `0 9 * * * cd /path/to/scraper && python bizbuysell_scraper.py`

### Option 2: Task Scheduler (Windows)

- Create a scheduled task to run `python bizbuysell_scraper.py` daily

### Option 3: GitHub Actions (Cloud)

- Upload to GitHub
- Add Google credentials as a secret
- The workflow will run daily automatically

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed scheduling instructions.

## Troubleshooting

**No data appearing?**
- BizBuySell may have changed their HTML structure
- Try the Selenium version: `python bizbuysell_scraper_selenium.py`
- Check if you're being rate-limited

**Google Sheets error?**
- Verify `credentials.json` is in the same directory
- Make sure you shared your sheet with the service account email
- Check that both APIs are enabled in Google Cloud

**Website blocking?**
- Increase delay between requests
- The scraper already includes 2-second delays
- Consider running during off-peak hours

## Important Notes

⚠️ **Legal & Ethical Use**
- Review BizBuySell's Terms of Service
- This is for personal research only
- Don't overwhelm their servers (delays are built-in)
- Don't redistribute scraped data commercially

⚠️ **Maintenance**
- Websites change their structure frequently
- You may need to update selectors if BizBuySell redesigns
- Test regularly to ensure it's still working

## Which Scraper Should I Use?

**Use `bizbuysell_scraper.py` (Basic)** if:
- You want a simple, lightweight solution
- The website loads content in plain HTML
- Faster execution is important

**Use `bizbuysell_scraper_selenium.py` (Advanced)** if:
- The basic scraper isn't finding listings
- BizBuySell uses heavy JavaScript
- You need to interact with dynamic elements

## Support

For detailed help with:
- Google Cloud setup
- Scheduling automation
- Customizing counties or filters
- Error troubleshooting

See **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)**

## License

This project is provided as-is for educational and personal use. Always respect website terms of service and robots.txt files.

---

**Created for scraping business listings in NC counties: Iredell, Cabarrus, Rowan, Catawba, Gaston, Lincoln, and Mecklenburg**
