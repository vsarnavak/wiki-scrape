import requests
from bs4 import BeautifulSoup
import re

def is_article_valid(url, min_length=1000, min_sections=5, min_images=2, min_citations=10):
    """
    Checks if a Wikipedia article meets a set of criteria based on its content.

    Args:
        url (str): The URL of the Wikipedia article.
        min_length (int): The minimum length of the article body (in characters).
        min_sections (int): The minimum number of sections.
        min_images (int): The minimum number of images.
        min_citations (int): The minimum number of citations/references.

    Returns:
        bool: True if the article meets all criteria, False otherwise.
    """
    try:
        # Fetch the Wikipedia page content
        headers = {'User-Agent': 'assamese_link_retriever'}
        response = requests.get(url, timeout=10, headers = headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 1. Filter by Article Length ---
        # Get all paragraph text and calculate length
        article_text = " ".join([p.get_text() for p in soup.find_all('p')])
        length = len(article_text)
        length_check = length >= min_length
        print(f"Article length: {length} characters. Pass? {length_check}")

        # --- 2. Filter by Number of Sections ---
        # Find all section headings (h2, h3, etc.)
        sections = soup.find_all(re.compile('^h[2-6]$'))
        sections_count = len(sections)
        sections_check = sections_count >= min_sections
        print(f"Number of sections: {sections_count}. Pass? {sections_check}")

        # --- 3. Filter by Presence of Infoboxes/Images ---
        # Check for infobox
        infobox_exists = soup.find('table', class_='infobox') is not None
        # Count images within the main content area
        images_count = len(soup.find_all('img'))
        images_check = images_count >= min_images
        infobox_images_check = infobox_exists and images_check
        print(f"Infobox exists? {infobox_exists}. Number of images: {images_count}. Pass? {infobox_images_check}")
        
        # --- 4. Filter by Number of Citations/References ---
        # Citations are typically links with class 'reference' or similar
        # Find all list items in the 'References' section
        citations_section = soup.find(id=re.compile("References|Citations|Notes"))
        citations_count = 0
        if citations_section:
            citations_list = citations_section.find_next('ol')
            if citations_list:
                citations_count = len(citations_list.find_all('li'))
        
        citations_check = citations_count >= min_citations
        # print(f"Number of citations: {citations_count}. Pass? {citations_check}")

        # Combine all checks
        return length_check and sections_check and infobox_images_check # and citations_check

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    # Replace these URLs with the Wikipedia links you want to filter
    wikipedia_links = [
        "https://en.wikipedia.org/wiki/States_and_union_territories_of_India",
        "https://bn.wikipedia.org/wiki/%E0%A6%B9%E0%A6%BE%E0%A6%B8%E0%A6%BF", # This article may not pass some filters
    ]

    for link in wikipedia_links:
        print(f"\n--- Checking article: {link} ---")
        if is_article_valid(link):
            print(f"✅ The article passes all filters.")
        else:
            print(f"❌ The article does not meet the criteria.")