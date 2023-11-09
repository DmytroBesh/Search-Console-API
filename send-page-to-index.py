import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import csv

# Setting up your domain
YOUR_DOMAIN = 'fondy.ua'

# Full path to the file from the URL
FILE_PATH = r'C:\Users\named\Розробка\Search Console API'

# Path to the file with service account keys
SERVICE_ACCOUNT_FILE = os.path.join(FILE_PATH, 'client_secret.json')

# Path to the .csv file to record the results
CSV_FILE_PATH = os.path.join(FILE_PATH, f'submission_results-{YOUR_DOMAIN}.csv')

# Creating credentials for Google API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/indexing']
)

# Creating a service for using the Google Search Console API
service = build('indexing', 'v3', credentials=credentials)

# Reading the URL from a file
with open(os.path.join(FILE_PATH, f'{YOUR_DOMAIN}_non_indexed_urls.txt'), 'r') as file:
    urls_to_index = [url.strip() for url in file.readlines()]

# Limit the number of URLs to 200
urls_to_index = urls_to_index[:200]

# Function for sending URLs for indexing
def submit_url(url):
    # Use the Indexing API method to send URLs for indexing
    body = {'url': url, 'type': 'URL_UPDATED'}
    response = service.urlNotifications().publish(body=body).execute()
    return response

# Open the .csv file to record the results
with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Headers for the .csv file, if the file does not already exist
    if file.tell() == 0:
        writer.writerow(['URL', 'Status', 'Detail'])

    # We send the URL for indexing with a delay of 1 second between requests
    for url in urls_to_index:
        try:
            full_url = f'https://{YOUR_DOMAIN}/{url}'
            response = submit_url(full_url)
            print(f'Submitted {url}: {response}')
            writer.writerow([full_url, 'Submitted', response])
        except Exception as e:
            print(f'Error submitting {url}: {e}')
            writer.writerow([f'https://{YOUR_DOMAIN}/{url}', 'Error', str(e)])
        time.sleep(1)  # Delay between URL sends

print(f'Total URLs submitted: {len(urls_to_index)}')