import fitz  # PyMuPDF
import os
from bs4 import BeautifulSoup
import re

def extract_html_with_regex(html_content, start_words, end_words):
    """
    Extracts HTML content between the specified start and end words.
    
    Args:
        html_content (str): The full HTML content as a string.
        start_words (list): A list of the first three words.
        end_words (list): A list of the last three words.
        
    Returns:
        str: The extracted HTML content, or None if no match is found.
    """
    # Create the regex pattern dynamically from the word lists
    start_pattern = f"{re.escape(start_words[0])}\\s*.*?{re.escape(start_words[1])}\\s*.*?{re.escape(start_words[2])}"
    end_pattern = f"{re.escape(end_words[0])}\\s*.*?{re.escape(end_words[1])}\\s*.*?{re.escape(end_words[2])}"
    
    # Combine patterns with a non-greedy match for the content in between
    regex_pattern = f"({start_pattern})((?:.|\\s)*?){end_pattern}"
    
    # The 're.DOTALL' flag allows '.' to match newlines
    match = re.search(regex_pattern, html_content, re.DOTALL)
    
    if match:
        # The content is in the second capturing group
        return match.group(2)
    else:
        return None


def process_pdf_and_html(pdf_path, html_path, output_folder):
    """
    Extracts HTML content corresponding to each page of a text-searchable PDF.
    
    Args:
        pdf_path (str): Path to the text-searchable PDF file.
        html_path (str): Path to the full HTML file.
        output_folder (str): Directory to save the extracted files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF document
    doc = fitz.open(pdf_path)

    # Read the full HTML content
    with open(html_path, 'r', encoding='utf-8') as f:
        full_html = f.read()

    # Use BeautifulSoup to parse the HTML for more robust searching
    soup = BeautifulSoup(full_html, 'html.parser')
    html_text = soup.get_text()

    # Process each page
    for i, page in enumerate(doc):
        page_number = i + 1
        page_text = page.get_text().strip()
        print(page_text)
        print('----------------')

        if not page_text:
            continue

        words = page_text.split()
        if len(words) < 6:  # Ensure there are enough words for a 3-word phrase at both ends
            print(f"Page {page_number} has too few words to form a 3-word boundary. Skipping.")
            continue

        first_phrase = " ".join(words[:3])
        last_phrase = " ".join(words[-3:])

        # Find the start and end of the text in the main HTML content
        try:
            html_txt = extract_html_with_regex(full_html, first_phrase, last_phrase)
            
            if html_txt is not None:
                # Get the content between the start and end words from the original HTML

                # Save the new HTML file
                html_filename = os.path.join(output_folder, f'page_{page_number}.html')
                with open(html_filename, 'w', encoding='utf-8') as f:
                    f.write(html_txt)
                
                print(f"Successfully extracted content for page {page_number}")
            else:
                print(f"Could not find matching text for page {page_number}")

        except Exception as e:
            print(f"An error occurred for page {page_number}: {e}")

# Example usage
pdf_file = 'test.pdf'
html_file = 'test.html'
output_dir = 'extracted_html'
process_pdf_and_html(pdf_file, html_file, output_dir)