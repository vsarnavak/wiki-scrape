import pandas as pd
import numpy as np
import base64
df = pd.read_csv("domain-csvs/culture.csv")

# To count null rows

# count = 0
# for index, row in df.iterrows():
#     if pd.isna(row['wikipedia_link']):
#         count += 1

# print(count)

# To keep and remove null rows

# df = pd.read_csv('domain-csvs/education.csv')

# # Drop rows where the 'wikipedia_link' column has a missing value (NaN)
# df_cleaned = df.dropna(subset=['wikipedia_link'])

# df_test = df[df['wikipedia_link'].isnull()]

# # You can now save the cleaned DataFrame to a new CSV file
# df_test.to_csv('bad_rows.csv', index = False)
# df_cleaned.to_csv('cleaned_data.csv', index=False)

# lang_codes = ["as", "bn", "gu", "hi", "kn", "ml", "mr", "or", "ta", "te"]
# domains = ["geography", "culture", "demography", "history", "economy", "education", "tourism", "politics"]

# df = pd.read_csv('master.csv')

# for code in lang_codes:
#     print(code, ':', df[f'{code}_wiki_link'].count())


# for code in lang_codes:
#     count = Geography[code] + Culture[code] + Demography[code] + History[code] + Economy[code] + Education[code] + Tourism[code] + Politics[code]
#     print(code, ':', count)

def extract_content_with_hardcoded_tables(page, num_columns, table_width_ratio) -> str:
    """
    Extracts text from a page with both multi-column layouts and full-width tables
    using a hardcoded width threshold to detect tables.

    Args:
        page (fitz.Page): The PyMuPDF page object.
        num_columns (int): The number of columns on the page.
        table_width_ratio (float): The ratio of page width that a block must exceed to be considered a table.
                                  A value of 0.8 means any block wider than 80% of the page is a table.

    Returns:
        str: The extracted text in the correct reading order.
    """
    page_rect = page.rect
    page_width = page_rect.width
    table_threshold = page_width * table_width_ratio

    full_text = ""
    
    # Get all text blocks and sort them vertically
    blocks = page.get_text("blocks")
    blocks.sort(key=lambda b: (b[1], b[0])) # Sort by y0 then x0 for a natural read flow

    column_blocks = []
    
    for block in blocks:
        block_rect = fitz.Rect(block[:4])
        block_text = block[4]
        
        # If the block is wide, it is likely a table or a heading spanning multiple columns.
        if block_rect.width > table_threshold:
            # Process any pending column blocks first, then the wide block
            if column_blocks:
                column_blocks.sort(key=lambda b: b[0])
                for col_b in column_blocks:
                    full_text += col_b[4]
                full_text += "\n"
                column_blocks = []
            
            full_text += block_text + "\n"
        else:
            # It's a column block, add it to a list for horizontal sorting
            column_blocks.append(block)
    
    # Process any remaining column blocks at the end
    if column_blocks:
        column_blocks.sort(key=lambda b: b[0])
        for col_b in column_blocks:
            full_text += col_b[4]
    
    return full_text


def extract_sorted_columns(page, num_columns):
    """
    Extracts text from a page with multiple columns in the correct reading order.

    Args:
        page (fitz.Page): The PyMuPDF page object.
        num_columns (int): The number of columns on the page.

    Returns:
        str: The extracted text in the correct reading order.
    """
    # Get the bounding box of the page
    page_rect = page.rect
    total_width = page_rect.width
    column_width = total_width / num_columns

    full_text = ""
    # Process each column strip from left to right
    for i in range(num_columns):
        # Define the bounding box for the current column
        column_rect = fitz.Rect(
            page_rect.x0 + i * column_width,
            page_rect.y0,
            page_rect.x0 + (i + 1) * column_width,
            page_rect.y1,
        )

        # Extract text from the column's bounding box, sorting it
        column_text = page.get_text(
            "text", clip=column_rect, sort=True
        )

        # Append the extracted text to the full text
        full_text += column_text + "\n"

    return full_text


from markdownify import markdownify as md
import fitz
import re

with open('test2.html', 'r', encoding='utf-8') as f:
    html_doc = f.read()
    match = re.search(r'column-count:\s*(\d+);', html_doc)
    if match:
        num_columns = int(match.group(1))
    else:
        num_columns = 1
        print("Error with col count")


markd = md(html_doc, strip=['a', 'img'])

# with open('test.md', 'w', encoding='utf-8') as f:
#     f.write(markd)

file_path = "test2.pdf"  # Replace with the path to your PDF
doc = fitz.open(file_path)

# num_columns = 2
co = 1
# Iterate through each page
for page in doc:
    print("Page", co)
    with open(f'fitz2/page_{co}.txt', 'w', encoding='utf-8') as f:
        # text = extract_sorted_columns(page, num_columns)
        text = extract_content_with_hardcoded_tables(page, num_columns, 0.8)
        
        f.write(text)
    co += 1

# print(markd)