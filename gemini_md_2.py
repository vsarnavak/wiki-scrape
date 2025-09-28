# html_to_markdown.py
#
# This script processes a Wikipedia HTML file and its corresponding PDF
# to create a single Markdown file, with content grouped by PDF page number.
#
# It requires the following libraries. You can install them using pip:
# pip install beautifulsoup4 pypdfium2-py markdownify

import os
from bs4 import BeautifulSoup
import pypdfium2 as pdfium
import markdownify

def process_html_elements(html_filepath):
    """
    Parses an HTML file and extracts a list of semantic elements and their text.

    Args:
        html_filepath (str): The path to the HTML file.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
              'tag_name' and 'text' of a semantic element.
    """
    elements = []
    try:
        with open(html_filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        # Find the main content area of a typical Wikipedia page
        content_div = soup.find(id="content")

        if content_div:
            # Iterate through the content and extract relevant elements in order.
            for tag in content_div.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                elements.append({
                    'tag_name': tag.name,
                    'text': tag.get_text(strip=True)
                })
        print(f"Successfully processed {len(elements)} elements from HTML.")
    except FileNotFoundError:
        print(f"Error: HTML file not found at {html_filepath}")
    return elements

def extract_pdf_pages_text(pdf_filepath):
    """
    Extracts raw text from each page of a PDF file.

    Args:
        pdf_filepath (str): The path to the PDF file.

    Returns:
        dict: A dictionary mapping page numbers (1-indexed) to their raw text.
    """
    pdf_text = {}
    try:
        # We use pypdfium2 for robust PDF text extraction.
        # It's an excellent choice for a wide range of PDFs.
        pdf = pdfium.PdfDocument(pdf_filepath)
        for i in range(len(pdf)):
            page = pdf[i]
            textpage = page.get_textpage()
            pdf_text[i + 1] = textpage.get_text_range()
        print(f"Successfully extracted text from {len(pdf_text)} PDF pages.")
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_filepath}")
    return pdf_text

def map_elements_to_pages(html_elements, pdf_text):
    """
    Maps each HTML element to the PDF page number where its text appears.

    Args:
        html_elements (list): The ordered list of HTML element dictionaries.
        pdf_text (dict): A dictionary of PDF page texts.

    Returns:
        list: A list of dictionaries, where each contains the original
              HTML element info and its corresponding 'page_number'.
    """
    mapped_content = []
    last_found_page = 1

    for element in html_elements:
        element_text = element['text'].strip()

        # If the text is empty, skip it.
        if not element_text:
            continue

        found_page = None
        # Start searching from the last known page to be more efficient,
        # as content is likely to be sequential.
        for page_num in range(last_found_page, len(pdf_text) + 1):
            if element_text in pdf_text[page_num]:
                found_page = page_num
                last_found_page = page_num
                break
        
        # If not found in subsequent pages, check from the beginning.
        # This handles cases where content might jump back, though
        # it's unlikely in this scenario.
        if found_page is None:
            for page_num in range(1, len(pdf_text) + 1):
                if element_text in pdf_text[page_num]:
                    found_page = page_num
                    last_found_page = page_num
                    break
        
        if found_page is not None:
            mapped_content.append({
                'tag_name': element['tag_name'],
                'text': element['text'],
                'page_number': found_page
            })
    
    print(f"Successfully mapped {len(mapped_content)} elements to PDF pages.")
    return mapped_content

def reconstruct_markdown(mapped_content):
    """
    Builds a single Markdown string from the mapped content,
    with page numbers as headers.

    Args:
        mapped_content (list): The list of mapped elements.

    Returns:
        str: The final Markdown content.
    """
    markdown_output = []
    current_page = None

    for item in mapped_content:
        if item['page_number'] != current_page:
            # New page, add a Markdown header.
            markdown_output.append(f"\n# Page {item['page_number']}\n")
            current_page = item['page_number']

        # Use markdownify to convert the element to Markdown.
        # We handle paragraphs and list items slightly differently for formatting.
        if item['tag_name'] == 'p':
            markdown_output.append(item['text'] + '\n\n')
        elif item['tag_name'] == 'li':
            markdown_output.append(f"* {item['text']}\n")
        else:
            # Use markdownify's built-in converter for headers.
            md_text = markdownify.markdownify(f"<{item['tag_name']}>{item['text']}</{item['tag_name']}>")
            markdown_output.append(md_text)

    return "".join(markdown_output)

def main(html_filepath, pdf_filepath, output_filepath):
    """
    Main function to orchestrate the entire process.
    """
    print("Starting processing...")

    # Step 1: Process HTML
    html_elements = process_html_elements(html_filepath)
    if not html_elements:
        print("No HTML elements to process. Exiting.")
        return

    # Step 2: Process PDF
    pdf_text = extract_pdf_pages_text(pdf_filepath)
    if not pdf_text:
        print("No text extracted from PDF. Exiting.")
        return

    # Step 3: Map & Match
    mapped_content = map_elements_to_pages(html_elements, pdf_text)

    # Step 4: Reconstruct Markdown
    markdown_output = reconstruct_markdown(mapped_content)

    # Write to a new Markdown file
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"Process complete! Output written to {output_filepath}")


if __name__ == '__main__':
    # --- UPDATE THESE FILE PATHS WITH YOUR ACTUAL FILES ---
    # Example usage with placeholder file paths.
    html_file = 'test.html'
    pdf_file = 'test.pdf'
    output_file = 'output.md'

    main(html_file, pdf_file, output_file)