import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import csv

#https://console.cloud.google.com/apis/api/indexing.googleapis.com/metrics?project=search-console-354907

# Setting up your domain
YOUR_DOMAIN = 'fondy.ua'

# Full path to the file from the URL
FILE_PATH = r'C:\Users\named\Розробка\Search Console API'

# Path to the file with service account keys
SERVICE_ACCOUNT_FILE = os.path.join(FILE_PATH, 'client_secret.json')

# Path to the .csv file to record the results
CSV_FILE_PATH = os.path.join(FILE_PATH, f'Projects/submission_results-{YOUR_DOMAIN}.csv')

# Creating credentials for Google API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/indexing']
)

# Creating a service for using the Google Search Console API
service = build('indexing', 'v3', credentials=credentials)

# Reading the URL from a file
url_file_path = os.path.join(FILE_PATH, f'Projects/{YOUR_DOMAIN}_non_indexed_urls.txt')
with open(url_file_path, 'r') as file:
    all_urls = [url.strip() for url in file.readlines()]

# Limit the number of URLs to 200
urls_to_index = all_urls[:200] 

# Function for sending URLs for indexing
def submit_url(url):
    # Use the Indexing API method to send URLs for indexing
    body = {'url': url, 'type': 'URL_UPDATED'}
    response = service.urlNotifications().publish(body=body).execute()
    return response

# List to keep track of successfully indexed URLs
successfully_indexed = []

# Open the .csv file to record the results
with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Headers for the .csv file, if the file does not already exist
    if file.tell() == 0:
        writer.writerow(['URL', 'Status', 'Detail'])

    # We send the URL for indexing with a delay of 1 second between requests
    for url in urls_to_index:
        try:
            if YOUR_DOMAIN not in url:
                full_url = f'https://{YOUR_DOMAIN}/{url}'
            else:
                full_url = url
            response = submit_url(full_url)
            print(f'Submitted {url}: {response}')
            writer.writerow([full_url, 'Submitted', response])
            # Assuming that if 'urlNotificationMetadata' in response, the URL is considered successfully indexed
            if 'urlNotificationMetadata' in response:
                successfully_indexed.append(url)
        except Exception as e:
            print(f'Error submitting {url}: {e}')
            writer.writerow([full_url, 'Error', str(e)])
        time.sleep(1)  # Delay between URL sends

# Rewrite the file excluding successfully indexed URLs
with open(url_file_path, 'w') as file:
    urls_to_keep = [url for url in all_urls if url not in urls_to_index]
    for url in urls_to_keep:
        file.write(url + '\n')

print(f'Total URLs submitted: {len(successfully_indexed)}')
