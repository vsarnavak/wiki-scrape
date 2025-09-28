import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import collections

def get_assamese_wiki_links(page_url, lang): # , filename
    try:
        # Send a GET request to the page
        headers = {'User-Agent': 'assamese_link_retriever'}
        response = requests.get(page_url, headers = headers)

        # html_content = response.text
        # Specify the file name
        # file_name = f"html_files/as_links/{filename}.html"

        # # Open the file in write mode and save the content
        # with open(file_name, "w", encoding="utf-8") as file:
        #     file.write(html_content)
        # Raise an exception for bad status codes
        response.raise_for_status()
        # Parse the page content with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags (<a>) which contain hyperlinks
        links = soup.find_all('a')
        
        assamese_links = set()  # Use a set to avoid duplicate links

        for link in links:
            href = link.get('href')
            # Check if the link is an internal wiki link
            if href and href.startswith('/wiki/') and ':' not in href:
                # Construct the full URL and add it to the set
                full_url = f"https://{lang}.wikipedia.org{href}"
                assamese_links.add(full_url)
                
        return sorted(list(assamese_links))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

# Example usage: Replace with your desired Assamese Wikipedia page URL

lang = 'or'

df = pd.read_csv(f'lang_links/{lang}_links.csv')
# df = df[500:]

total_links = df[f'{lang}_wiki_link']
# urls_to_visit = collections.deque([total_links])
unique = set(total_links)
total_links = list(total_links)

while total_links:
    url = total_links.pop(0)
    if pd.isna(url):
        continue
    # keyw = row['Keyword']
    # keyw.replace(' ', '_')
    print(f"Retrieving {lang} page from {url}") # {keyw}
    found_links = get_assamese_wiki_links(url, lang) # keyw
    for link in found_links:
        if link not in unique:
            unique.add(link)
            total_links.append(link)

    time.sleep(0.3)


final_links = list(unique)

# df2 = pd.read_csv(f'lang_links/{lang}_links.csv')
df2 = pd.DataFrame()
df2[f'{lang}_wiki_link'] =  final_links

df2.to_csv(f'lang_links/{lang}_links_2.csv', index = False)

# # page_to_scrape = "https://as.wikipedia.org/wiki/ভাৰত"
# # found_links = get_assamese_wiki_links(page_to_scrape)
# count = 0
# oc = 0
# # df = df[:100]
# # for link in df['as_wiki_link']:
# #     print(link)

# if found_links:
#     print("Found the following internal Assamese Wikipedia links:")
#     for link in found_links:
#         if link.split('.')[0][-2:] != 'as':
#             oc += 1

#         if df['as_wiki_link'].str.contains(link).any():
#             count += 1
#         # print(link)
#     print(len(found_links))
# else:
#     print("No links found or an error occurred.")

# print("Number of new links :", count)
# print("Non as links :", oc)