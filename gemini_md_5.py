import html2text
from bs4 import BeautifulSoup
from thefuzz import fuzz
from difflib import SequenceMatcher as SM
from nltk.util import ngrams
import codecs

def find_best_match(text_line, html_blocks):
    """
    Finds the best matching HTML block for a given text line using fuzzy matching.
    Returns the original HTML block and its text content.
    """
    # 1. First, check for an exact substring match
    for block in html_blocks:
        html_text = block.get_text(strip=True).replace("\n", " ")
        if text_line.lower() in html_text.lower():
            # Found an exact substring match, return immediately
            return block, 100, html_text

    # 2. If no exact substring match, fall back to fuzzy matching
    best_score = 0
    best_match = None
    best_match_text = ""

    for block in html_blocks:
        html_text = block.get_text(strip=True).replace("\n", " ")

        needle = text_line.lower()
        hay = html_text.lower()
        needle_length  = len(needle.split())
        max_sim_val    = 0
        max_sim_string = u""

        for ngram in ngrams(hay.split(), needle_length + int(.2*needle_length)):
            hay_ngram = u" ".join(ngram)
            similarity = SM(None, hay_ngram, needle).ratio() 
            if similarity > max_sim_val:
                max_sim_val = similarity
                max_sim_string = hay_ngram

        # If the similarity is higher than prev blocks, make this the new best match
        if max_sim_val > best_score:
            best_score = max_sim_val
            best_match = block
            best_match_text = max_sim_string

        # score = fuzz.ratio(text_line.lower(), html_text.lower())
        # if score > best_score:
        #     best_score = score
        #     best_match = block
        #     best_match_text = html_text

    return best_match, best_score, best_match_text

def process_files(text_file_path, html_file_path, output_file_path):
    """
    Main function to process the text and HTML files.
    """
    try:
        # Load the HTML content
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all potential text blocks
        html_blocks = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote'])
        
        # Load the text file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_lines = [line.strip() for line in f if line.strip()]

        # Prepare for markdown output
        h = html2text.HTML2Text()
        h.body_width = 0 # Prevent line wrapping

        # Process each text line
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for i, line in enumerate(text_lines):
                if not line:
                    continue

                best_match_block, score, best_match_text = find_best_match(line, html_blocks)
                
                # Set a similarity threshold, for example 80%
                if score >= 0 and best_match_block:
                    markdown_content = h.handle(str(best_match_block))
                    
                    outfile.write(f"### Match {i+1} 🚀\n")
                    outfile.write(f"**Original Text Line:** `{line}`\n")
                    outfile.write(f"**Fuzzy Match Score:** `{score}%`\n")
                    outfile.write(f"**Best Matched HTML Text:** `{best_match_text}`\n")
                    outfile.write(f"**Converted Markdown:**\n")
                    outfile.write(f"```markdown\n{markdown_content.strip()}\n```\n\n---\n")
                else:
                    outfile.write(f"### No Match Found for Line {i+1} 🤷‍♀️\n")
                    outfile.write(f"**Original Text Line:** `{line}`\n\n---\n")

        print(f"✅ Processing complete! Results saved to `{output_file_path}`.")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}. Please check your file paths.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")



# Run the function with your file paths
process_files('fitz2/page_1.txt', 'test.html', 'output.md')