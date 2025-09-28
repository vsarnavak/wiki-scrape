import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
from pypdf import PdfReader
from difflib import SequenceMatcher
import os
import time
import fitz

def find_best_match(block_text, pdf_text):
    """
    Finds the best matching substring in pdf_text for a given block_text.
    Returns the highest match score and the corresponding substring.
    """
    block_length = len(block_text)
    best_score = 0
    best_match_text = ""

    # Iterate through pdf_text with a sliding window of the same length as block_text
    for i in range(0, len(pdf_text) - block_length + 1, 3):
        window = pdf_text[i:i + block_length]

        # Calculate the similarity ratio
        score = SequenceMatcher(None, block_text, window).ratio()

        # Update the best score and text if the current score is higher
        if score > best_score:
            best_score = score
            best_match_text = window
        if score > 0.8:
            break
    
    return best_score, best_match_text



async def save_paged_html(url, output_dir='paged_html'):
    """
    Converts a single HTML document from a URL into multiple HTML files,
    one for each page of the generated PDF.
    """
    
    # 1. Setup pyppeteer and generate the PDF
    # browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    # page = await browser.newPage()
    
    try:
        # await page.goto(url, {'waitUntil': 'networkidle0'})
        
        # Get the full HTML and generate PDF
        # full_html = await page.content()
        
        # await page.pdf({'path': pdf_path, 'format': 'Letter'})
        print("1. Parsing HTML into semantic blocks...")
        with open('test.html', 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # 2. Parse the PDF for page-specific text
        print("2. Parsing PDF to get page text markers...")
        pdf_path = 'test.pdf'
        # reader = PdfReader(pdf_path)
        doc = fitz.open(pdf_path)
        # pdf_pages_text = [p.extract_text() for p in reader.pages]
        pdf_pages_text = [p.get_text() for p in doc]
        
        # soup = BeautifulSoup(full_html, 'html.parser')
        
        # Define the tags we want to process
        tags_to_process = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'table']
        html_blocks = soup.find_all(tags_to_process)
        
        # Initialize an array of strings, one for each page's HTML content
        page_html_content = ["" for _ in range(len(pdf_pages_text) + 1)]
        
        # 4. Match HTML blocks to PDF pages and build the HTML content
        print("4. Matching HTML blocks to PDF pages...")
        for block in html_blocks:
            # Get the text of the HTML block
            block_text = block.get_text(strip=True)
            if not block_text:
                continue

            best_match_page = -1
            highest_score = 0.0
            
            # Find the best matching page for the current block
            for i, pdf_text in enumerate(pdf_pages_text):
                # Use SequenceMatcher for a robust similarity check
                # match_score = SequenceMatcher(None, block_text, pdf_text).ratio()
                
                # We need a better method. Let's try matching a substring.
                if block_text in pdf_text:
                    best_match_page = i
                    break # Found a perfect match, no need to check further
                else:
                    best_score, best_match_text = find_best_match(block_text, pdf_text)
                    if best_score > 0.8:
                        best_match_page = i
                        break
                
            # If no perfect match found, use a heuristic
            if best_match_page == -1:
                for i, pdf_text in enumerate(pdf_pages_text):
                    if block_text[:min(50, len(block_text))] in pdf_text:
                        best_match_page = i
                        break

            if best_match_page != -1:
                page_html_content[best_match_page] += str(block) + '\n'
            else:
                # If no match is found, append to the last page as a fallback
                page_html_content[-1] += str(block) + '\n'

        # 5. Save the individual HTML files
        print("5. Saving individual HTML files...")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        for i, html_content in enumerate(page_html_content):
            file_path = os.path.join(output_dir, f'page_{i + 1}.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<!DOCTYPE html>\n<html>\n<body>\n')
                f.write(html_content)
                f.write('</body>\n</html>')
            print(f"   - Saved {file_path}")
            
    finally:
        pass
        # Clean up temporary files
        # await browser.close()
        # if os.path.exists(pdf_path):
        #     os.remove(pdf_path)

# Example Usage:
async def main():
    url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    start_time = time.time()
    await save_paged_html(url)
    end_time = time.time()

    print("Time taken:", end_time - start_time)

if __name__ == '__main__':
    asyncio.run(main())