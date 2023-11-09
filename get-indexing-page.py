import os
import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

# Setting up your domain
domain_name = 'fondy.ua'
# Full path to the file from the URL
FILE_PATH = 'C:/Users/named/Розробка/Search Console API'

# Function to get all sitemaps from the robots.txt file
def get_sitemaps_from_robots(domain_name):
    robots_url = f'https://{domain_name}/robots.txt'
    response = requests.get(robots_url)
    if response.status_code == 200:
        sitemaps = []
        for line in response.text.splitlines():
            if line.startswith('Sitemap:'):
                sitemap_url = line.split(' ')[1]
                sitemaps.append(sitemap_url)
        return sitemaps
    else:
        print("Error fetching robots.txt")
        return []

# Recursive function to get URLs from sitemaps, including nested sitemaps
def fetch_all_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        sitemap_content = ET.fromstring(response.content)
        urls = []

        for sitemap_tag in sitemap_content:
            tag_url = sitemap_tag.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            if tag_url.endswith('.xml'):
                urls.extend(fetch_all_urls_from_sitemap(tag_url))
            else:
                urls.append(tag_url)
        return urls
    else:
        print(f"Error fetching sitemap: {sitemap_url}")
        return []

# Function to get indexed URLs via Google Search Console API
def fetch_indexed_urls(service, domain_name):
    site_url = f'sc-domain:{domain_name}'
    indexed_urls = []
    startRow = 0
    numRows = 1000
    endDate = datetime.now(timezone.utc).date() 
    startDate = endDate - timedelta(days=28)

    while True:
        request = {
            'startDate': startDate.strftime('%Y-%m-%d'),
            'endDate': endDate.strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'rowLimit': numRows,
            'startRow': startRow
        }
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        if 'rows' not in response:
            break
        for row in response['rows']:
            url = row['keys'][0]
            indexed_urls.append(url)

        if len(response['rows']) < numRows:
            break
        startRow += numRows

    return indexed_urls

KEY_FILE_LOCATION = os.path.join(FILE_PATH, 'client_secret.json')
credentials = service_account.Credentials.from_service_account_file(
    KEY_FILE_LOCATION, scopes=['https://www.googleapis.com/auth/webmasters'])
service = build('webmasters', 'v3', credentials=credentials)

sitemaps = get_sitemaps_from_robots(domain_name)
all_site_urls = []
for sitemap_url in sitemaps:
    all_site_urls.extend(fetch_all_urls_from_sitemap(sitemap_url))

indexed_urls = fetch_indexed_urls(service, domain_name)
non_indexed_urls = sorted(set(all_site_urls) - set(indexed_urls))  # Sorting URLs

# Writing non-indexed URLs to a file
non_indexed_file_path = os.path.join(FILE_PATH, f'{domain_name}_non_indexed_urls.txt')
with open(non_indexed_file_path, 'w') as file:
    for url in non_indexed_urls:
        file.write(url + '\n')

# Display a simple success message on the terminal
print("Success")
print(f'Total non-indexed URLs written to file: {len(non_indexed_urls)}')
