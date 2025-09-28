import pdfplumber
import os

def extract_text_from_pdf_pages(pdf_path, output_folder):
    """
    Extracts text from each page of a PDF and saves each page's text to a separate file.

    Args:
        pdf_path (str): The path to the PDF file.
        output_folder (str): The name of the folder where the text files will be saved.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created directory: {output_folder}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Processing PDF: {pdf_path}")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()

                # Define the output file name
                file_name = f"page_{i + 1}.txt"
                file_path = os.path.join(output_folder, file_name)

                # Write the extracted text to the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text if text else "")
                
                print(f"Extracted text from page {i + 1} and saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage
if __name__ == "__main__":
    # Replace 'your_document.pdf' with the path to your PDF file
    pdf_file_path = 'test.pdf'
    
    # Replace 'extracted_pages' with your desired output folder name
    output_directory_name = 'extracted_pages'

    # Check if the PDF file exists before running the function
    if os.path.exists(pdf_file_path):
        extract_text_from_pdf_pages(pdf_file_path, output_directory_name)
    else:
        print(f"Error: The file '{pdf_file_path}' was not found.")
        print("Please make sure the PDF file is in the same directory as the script or provide the correct path.")