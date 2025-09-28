import os
from pdf2image import convert_from_path

# Set up paths
pdf_path = 'Food_Wikipedia.pdf'
html_path = 'Food_Wikipedia.html'
output_folder = 'extracted_pages'

# Make the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the full HTML content
with open(html_path, 'r', encoding='utf-8') as f:
    full_html = f.read()

# Convert PDF to images
images = convert_from_path(pdf_path)

# Iterate through each page/image
for i, image in enumerate(images):
    page_number = i + 1

    # Step 1: Save the image
    image_filename = os.path.join(output_folder, f'page_{page_number}.png')
    image.save(image_filename, 'PNG')
    
