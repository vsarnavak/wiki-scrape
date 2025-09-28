import asyncio
from pyppeteer import launch
import pandas as pd
import requests
import time
import os

# Set a delay to respect Wikipedia's rate limits (e.g., 1 second)
# Wikipedia suggests no more than one request per second.
DELAY = 1

# Define the folder to save the HTML files
HTML_FOLDER = 'html_files/tourism'
csv_folder = 'domain-csvs/tourism.csv'

# Create the folder if it doesn't exist
if not os.path.exists(HTML_FOLDER):
    os.makedirs(HTML_FOLDER)

# Load the CSV file
try:
    df = pd.read_csv(csv_folder)  # Replace 'your_file.csv' with your actual file name
except FileNotFoundError:
    print("Error: The CSV file was not found.")
    exit()

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    link = row['wikipedia_link']
    if pd.isna(row['wikipedia_link']):
        continue
    keyword = row['Keyword']

    # Create the filename from the keyword, replacing invalid characters
    filename = f"{keyword.replace('/', '_').replace(':', '_')}.html"
    filepath = os.path.join(HTML_FOLDER, filename)

    print(f"Downloading {link} to {filepath}...")

    try:
        # Send a GET request to the link
        response = requests.get(link, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Save the HTML content to a file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print("Download successful! ✅")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {link}: {e} ❌")
        # You might want to log the error or handle it differently

    # Pause for the specified delay to avoid hitting rate limits
    time.sleep(DELAY)

print("\nAll downloads complete.")