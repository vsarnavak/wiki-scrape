import asyncio
from pyppeteer import launch
import base64
import random
import os
import time
import pandas as pd

lang_code_mapping = {"as" : "assamese", "bn" : "bengali", "gu" : "gujarati", "hi" : "hindi","kn" : "kannada",
                    "ml" : "malayalam", "mr" : "marathi", "or" : "odia", "ta" : "tamil", "te" : "telugu"}

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

async def save_wikipedia_article_as_pdf(url, output_filename, domain, code):
    """
    Renders a Wikipedia article as a PDF.

    Args:
        url (str): The URL of the Wikipedia article.
        output_filename (str): The name of the output PDF file.
    """
    # Launch a headless Chromium browser instance
    global skipped_pages
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
    try:
        lang_code = url.split('.')[0][-2:]
        lang = lang_code_mapping[lang_code]
    except Exception as e:
        print("URL Error. Skipping")
        return
    paragraph_fonts_dir = os.path.join("fonts", lang, "Paragraph")
    paragraph_font_path = get_random_font(paragraph_fonts_dir)
    font_css = generate_font_css(paragraph_font_path, 'CustomFont')
    css_string = css_string.replace("--font--", font_css)

    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    browser = await launch(headless=True, executablePath = chrome_path)
    # Open a new page (tab) in the browser
    page = await browser.newPage()

    try:
        print(f"Navigating to {url}...")
        # Navigate to the specified URL
        try:
            await page.goto(url, {'waitUntil': 'networkidle0'})
        except Exception as e:
            print("Error loading page, skipping")
            skipped_pages.append(f"{output_filename}")
            return

        rand_width = random.randint(800, 1600)
        random_width = f'{rand_width}px'
        random_height = f'{random.randint(800, 1600)}px'
        # print(random_width, random_height)

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

        header_html = """
            <div style="font-size: 10px; width: 100%; margin: 0 20px; color: #555;">
                <span style="float: left;">My Company Document</span>
                <span style="float: right;">Confidential</span>
            </div>
        """
        footer_html = """
            <div style="font-size: 10px; width: 100%; margin: 0 20px; color: #555; text-align: right;">
                <span class="pageNumber"></span> / <span class="totalPages"></span>
            </div>
        """

        # await page.emulateMedia('screen') # Code to get the screen view instead of the print view


        # Generate the PDF with some print options
        pdf_path = f"scaled/{domain}/pdf/{code}/{output_filename}.pdf"
        await page.pdf({
            'path': pdf_path,
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
        print(f"Successfully saved PDF to {pdf_path}")

        # Save as HTML
        html_filename = f"scaled/{domain}/html/{code}/{output_filename}.html"
        html_content = await page.content()
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully saved HTML to {html_filename}")

    finally:
        # Close the browser
        await browser.close()


count = 0

df = pd.read_csv('master.csv')

# Manage current index in master csv file
df = df[337:]
global skipped_pages
skipped_pages = []
for index, row in df.iterrows():
    
    pdf_name = row['Keyword'].replace(' ', '_')
    domain = row['Domain']
    lang_codes = ["as", "bn", "gu", "hi", "kn", "ml", "mr", "or", "ta", "te"]
    for code in lang_codes:
        if not pd.isna(row[f"{code}_wiki_link"]):
            pdf_name2 = f"{pdf_name}_{code}"
            url = row[f"{code}_wiki_link"]
            # Run the asynchronous function
            asyncio.get_event_loop().run_until_complete(
                save_wikipedia_article_as_pdf(url, pdf_name2, domain, code)
            )
            time.sleep(0.5)

print("Skipped pages :", skipped_pages)