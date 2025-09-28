import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def extract_text_pdfminer(pdf_path, output_folder):
    """
    Extracts text page by page from a PDF using pdfminer.six and saves each page's 
    text to a separate file in the specified output folder.
    
    Args:
        pdf_path (str): The path to the PDF file.
        output_folder (str): The name of the folder where the text files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    try:
        # Loop through each page of the PDF
        for page_number, page_layout in enumerate(extract_pages(pdf_path)):
            page_text = []
            
            # Iterate through each text container on the page
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    # Append the text from the container to the list
                    page_text.append(element.get_text())

            # Join the extracted text into a single string for the page
            full_page_text = "".join(page_text)
            
            # Define the output file name and path
            file_name = f"page_{page_number + 1}.txt"
            file_path = os.path.join(output_folder, file_name)

            # Write the text to the file with UTF-8 encoding
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(full_page_text)
            
            print(f"Extracted text from page {page_number + 1} and saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage
if __name__ == "__main__":
    # Replace 'your_document.pdf' with the path to your PDF file
    pdf_file_path = 'test.pdf'
    
    # Replace 'extracted_pages_pdfminer' with your desired output folder name
    output_directory_name = 'extracted_pages_pdfminer'

    # Check if the PDF file exists before running the function
    if os.path.exists(pdf_file_path):
        extract_text_pdfminer(pdf_file_path, output_directory_name)
    else:
        print(f"Error: The file '{pdf_file_path}' was not found.")
        print("Please make sure the PDF file is in the same directory as the script or provide the correct path.")