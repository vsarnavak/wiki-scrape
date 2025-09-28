import asyncio
from pyppeteer import launch
import base64
import random
import os
from bs4 import BeautifulSoup

lang_code_mapping = {"as" : "assamese", "bn" : "bengali", "gu" : "gujarati", "hi" : "hindi","kn" : "kannada",
                    "ml" : "malayalam", "mr" : "marathi", "or" : "odia", "ta" : "tamil", "te" : "telugu"}

async def get_page_level_html(page, random_width, random_height):
    """
    Extract HTML content for each PDF page based on the same dimensions
    used for PDF generation.
    """
    
    # Convert mm to pixels (assuming 96 DPI)
    # 1mm = 3.7795275591 pixels at 96 DPI
    mm_to_px = 3.7795275591
    
    # Calculate margins in pixels
    margin_top = 10 * mm_to_px
    margin_right = 10 * mm_to_px
    margin_bottom = 10 * mm_to_px
    margin_left = 10 * mm_to_px
    
    # Convert width/height from your units to pixels if needed
    # Assuming random_width and random_height are already in pixels
    page_width = random_width
    page_height = random_height
    
    # Calculate content area (excluding margins)
    content_width = page_width - margin_left - margin_right
    content_height = page_height - margin_top - margin_bottom
    
    # Set viewport to match PDF dimensions
    await page.setViewport({
        'width': int(page_width),
        'height': int(page_height)
    })
    
    # Get all elements with their positions and HTML content
    elements_data = await page.evaluate(f'''
        () => {{
            const marginTop = {margin_top};
            const marginLeft = {margin_left};
            const contentHeight = {content_height};
            
            // Get all visible elements
            const allElements = Array.from(document.querySelectorAll('*')).filter(el => {{
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            }});
            
            const elementsData = allElements.map((el, index) => {{
                const rect = el.getBoundingClientRect();
                
                // Adjust for margins
                const adjustedTop = rect.top - marginTop;
                const adjustedLeft = rect.left - marginLeft;
                
                return {{
                    index: index,
                    tagName: el.tagName,
                    outerHTML: el.outerHTML,
                    innerHTML: el.innerHTML,
                    textContent: el.textContent,
                    top: adjustedTop,
                    left: adjustedLeft,
                    bottom: adjustedTop + rect.height,
                    right: adjustedLeft + rect.width,
                    width: rect.width,
                    height: rect.height,
                    className: el.className,
                    id: el.id
                }};
            }});
            
            return elementsData;
        }}
    ''')
    
    # Group elements by page
    pages_content = []
    current_page = 1
    current_page_elements = []
    
    # Sort elements by their vertical position
    elements_data.sort(key=lambda x: x['top'])
    
    for element in elements_data:
        # Check if element starts on current page
        element_page = max(1, int(element['top'] // content_height) + 1)
        
        # If we've moved to a new page, save current page and start new one
        if element_page > current_page:
            if current_page_elements:
                pages_content.append({
                    'page': current_page,
                    'elements': current_page_elements.copy(),
                    'html': create_page_html(current_page_elements)
                })
            current_page_elements = []
            current_page = element_page
        
        current_page_elements.append(element)
    
    # Don't forget the last page
    if current_page_elements:
        pages_content.append({
            'page': current_page,
            'elements': current_page_elements,
            'html': create_page_html(current_page_elements)
        })
    
    return pages_content

def create_page_html(elements):
    """
    Create HTML structure for a page from its elements.
    """
    if not elements:
        return ""
    
    # Get the original document structure
    html_elements = [el for el in elements if el['tagName'] == 'HTML']
    body_elements = [el for el in elements if el['tagName'] == 'BODY']
    
    # Start with basic structure
    page_html = "<!DOCTYPE html>\n<html>\n<head>\n"
    
    # Add head elements (style, meta, etc.)
    head_elements = [el for el in elements if el['tagName'] in ['STYLE', 'META', 'LINK', 'TITLE']]
    for el in head_elements:
        page_html += f"  {el['outerHTML']}\n"
    
    page_html += "</head>\n<body>\n"
    
    # Add body content elements (excluding html, head, body tags themselves)
    content_elements = [el for el in elements 
                       if el['tagName'] not in ['HTML', 'HEAD', 'BODY', 'STYLE', 'META', 'LINK', 'TITLE']]
    
    # Sort by position to maintain document flow
    content_elements.sort(key=lambda x: (x['top'], x['left']))
    
    for el in content_elements:
        page_html += f"  {el['outerHTML']}\n"
    
    page_html += "</body>\n</html>"
    
    return page_html

def clean_page_html(html_content):
    """
    Clean and format the HTML content for better readability.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.prettify()

async def extract_and_save_pages(page, random_width, random_height, output_dir="page_htmls"):
    """
    Extract page-level HTML and save to files.
    """
    import os
    print('Here')
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract page content
    pages_data = await get_page_level_html(page, random_width, random_height)
    
    # Save each page
    for page_data in pages_data:
        page_num = page_data['page']
        html_content = clean_page_html(page_data['html'])
        
        # Save to file
        filename = f"{output_dir}/page_{page_num:03d}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Saved page {page_num} with {len(page_data['elements'])} elements")
    
    return pages_data


##### My code after this. Before is Claude HTML page code

def get_random_font(fonts_dir):
    fonts_dir = os.path.abspath(fonts_dir)
    fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf')]
    if not fonts:
        raise FileNotFoundError(f"No .ttf files found in directory: {fonts_dir}")
    return os.path.join(fonts_dir, random.choice(fonts))

def generate_font_css(font_path, font_name):
    with open(font_path, "rb") as font_file:
        encoded_string = base64.b64encode(font_file.read()).decode('utf-8')
    
    return f"""
    @font-face {{
        font-family: '{font_name}';
        src: url('data:font/ttf;base64,{encoded_string}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    """

async def save_wikipedia_article_as_pdf(url, output_filename, chrome_path):
    """
    Renders a Wikipedia article as a PDF.

    Args:
        url (str): The URL of the Wikipedia article.
        output_filename (str): The name of the output PDF file.
    """
    # Launch a headless Chromium browser instance
    css_string = """
            --font--
            #content * {
                font-family: "CustomFont", serif !important;
                font-size: --fontsize--pt !important;
                line-height: 1.5;
            }
            #content h1, #content h2, #content h3 {
                font-family: "CustomFont", sans-serif !important;
                font-weight: bold;
            }
            #content {
                column-count: --columns--;
                column-gap: 2em;
            }
            .thumb, .infobox {
                break-inside: avoid-column;
            }
            .mw-logo { 
                display: none !important; 
            }
            /* Constrain all images to fit inside a column */
            #content img {
                max-width: 100%;
                height: auto;
                display: block;
            }
            /* For tables to span across the whole row instead of the 2 column layout */
            #content table {
                column-span: all;
                width: 100% !important;
                max-width: 100% !important;
                table-layout: auto !important;
            }
            /* For thumbnails and figure containers */
            .thumb, .thumbinner, figure {
                max-width: 100% !important;
            }
            
            """
    lang_code = url.split('.')[0][-2:]
    lang = lang_code_mapping[lang_code]
    paragraph_fonts_dir = os.path.join("fonts", lang, "Paragraph")
    paragraph_font_path = get_random_font(paragraph_fonts_dir)
    font_css = generate_font_css(paragraph_font_path, 'CustomFont')
    css_string = css_string.replace("--font--", font_css)

    
    browser = await launch(headless=True, executablePath = chrome_path)
    # Open a new page (tab) in the browser
    page = await browser.newPage()

    try:
        print(f"Navigating to {url}...")
        # Navigate to the specified URL
        await page.goto(url, {'waitUntil': 'networkidle0'})

        # await page.goto('file://E:/Projects/wiki-scrape/test.html', {'waitUntil': 'networkidle0'})

        # await page.emulateMedia('print')

        rand_width = random.randint(800, 1600)
        rand_height = random.randint(800, 1600)
        random_width = f'{rand_width}px'
        random_height = f'{rand_height}px'
        print(random_width, random_height)

        await page.pdf({
            'path': 'trial.pdf',
            'width': random_width, 
            'height': random_height,
            # 'format': 'A4',
            # 'displayHeaderFooter': True, 
            # 'headerTemplate': header_html,
            # 'footerTemplate': footer_html,
            'printBackground': True,  # This ensures images and colors are included
            'landscape': False, # Orientation of PDF pages
            'margin': {
                'top': '10mm',          # or '20mm'
                'right': '10mm',
                'bottom': '10mm',
                'left': '10mm'
            }
        })

        if rand_width > 1400:
            num_columns = random.choice([1,2,3,4])
        elif rand_width > 1200:
            num_columns = random.choice([1,2,3])
        elif rand_width > 1000:
            num_columns = random.choice([1,2])
        else:
            num_columns = 1
        font_size = random.randint(12,16)

        css_string = css_string.replace('--fontsize--', str(font_size))
        css_string = css_string.replace('--columns--', str(num_columns))
        # Make 2 column layout
        print("Injecting CSS")
        await page.addStyleTag({
            'content': css_string
        })

        # print("Making page by page HTML")
        # await extract_and_save_pages(page, rand_width, rand_height)

        # header_html = """
        #     <div style="font-size: 10px; width: 100%; margin: 0 20px; color: #555;">
        #         <span style="float: left;">My Company Document</span>
        #         <span style="float: right;">Confidential</span>
        #     </div>
        # """
        # footer_html = """
        #     <div style="font-size: 10px; width: 100%; margin: 0 20px; color: #555; text-align: right;">
        #         <span class="pageNumber"></span> / <span class="totalPages"></span>
        #     </div>
        # """

        # await page.emulateMedia('screen') # Code to get the screen view instead of the print view

        # Generate the PDF with some print options
        await page.pdf({
            'path': output_filename,
            'width': random_width, 
            'height': random_height,
            # 'format': 'A4',
            # 'displayHeaderFooter': True, 
            # 'headerTemplate': header_html,
            # 'footerTemplate': footer_html,
            'printBackground': True,  # This ensures images and colors are included
            'landscape': False, # Orientation of PDF pages
            'margin': {
                'top': '10mm',          # or '20mm'
                'right': '10mm',
                'bottom': '10mm',
                'left': '10mm'
            }
        })

        # print(pdf_string)
        print(f"Successfully saved PDF to {output_filename}")

        # Save as HTML
        output_f = output_filename.split('.')[0]
        html_filename = f"{output_f}.html"
        html_content = await page.content()
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully saved HTML to {html_filename}")

    finally:
        # Close the browser
        await browser.close()

# The URL of the Wikipedia article to save
article_url = 'https://bn.wikipedia.org/wiki/States_and_union_territories_of_India' # 'https://en.wikipedia.org/wiki/Arunachal_Pradesh' - https://en.wikipedia.org/wiki/States_and_union_territories_of_India
# The desired name for the output PDF file
pdf_output = 'test2.pdf'
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Run the asynchronous function
asyncio.get_event_loop().run_until_complete(
    save_wikipedia_article_as_pdf(article_url, pdf_output, chrome_path)
)