"""
Test script to verify your setup before running the full scraper
"""

import sys

print("Testing BizBuySell Scraper Setup...")
print("=" * 60)

# Test 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 7):
    print("   ⚠️  WARNING: Python 3.7+ recommended")
else:
    print("   ✓ Python version OK")

# Test 2: Required packages
print("\n2. Testing Required Packages:")
required_packages = {
    'requests': 'requests',
    'beautifulsoup4': 'bs4',
    'pandas': 'pandas',
    'gspread': 'gspread',
    'oauth2client': 'oauth2client'
}

missing_packages = []
for package_name, import_name in required_packages.items():
    try:
        __import__(import_name)
        print(f"   ✓ {package_name} installed")
    except ImportError:
        print(f"   ✗ {package_name} NOT installed")
        missing_packages.append(package_name)

if missing_packages:
    print(f"\n   To install missing packages, run:")
    print(f"   pip install {' '.join(missing_packages)}")
else:
    print("\n   ✓ All required packages installed")

# Test 3: Google credentials file
print("\n3. Testing Google Credentials:")
import os
if os.path.exists('credentials.json'):
    print("   ✓ credentials.json found")
    
    # Try to read it
    try:
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        if 'client_email' in creds:
            print(f"   ✓ Service account email: {creds['client_email']}")
        else:
            print("   ⚠️  WARNING: credentials.json doesn't look like a service account file")
            
    except Exception as e:
        print(f"   ⚠️  WARNING: Could not read credentials.json: {str(e)}")
else:
    print("   ✗ credentials.json NOT found")
    print("   Please follow the setup instructions to create this file")

# Test 4: Network connectivity
print("\n4. Testing Network Connection:")
try:
    import requests
    response = requests.get('https://www.bizbuysell.com', timeout=10)
    if response.status_code == 200:
        print("   ✓ Can connect to BizBuySell")
    else:
        print(f"   ⚠️  WARNING: BizBuySell returned status code {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to BizBuySell: {str(e)}")

# Test 5: Google Sheets API
print("\n5. Testing Google Sheets API:")
if os.path.exists('credentials.json'):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'credentials.json', scope)
        client = gspread.authorize(creds)
        
        print("   ✓ Google Sheets authentication successful")
        print("   ✓ Ready to update Google Sheets")
        
    except Exception as e:
        print(f"   ✗ Google Sheets authentication failed: {str(e)}")
        print("   Make sure you've enabled the Google Sheets API and shared your sheet")
else:
    print("   ⚠️  Skipping (credentials.json not found)")

# Summary
print("\n" + "=" * 60)
print("Setup Test Complete")
print("=" * 60)

if not missing_packages and os.path.exists('credentials.json'):
    print("\n✓ Your setup looks good! You can run the scraper with:")
    print("  python bizbuysell_scraper.py")
else:
    print("\n⚠️  Please address the issues above before running the scraper")
    print("  See SETUP_INSTRUCTIONS.md for detailed setup steps")
