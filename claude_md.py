#!/usr/bin/env python3
"""
Wikipedia HTML-PDF to Markdown Extractor

This script extracts semantically-structured markdown from Wikipedia pages
by combining HTML semantic structure with PDF page-level text segmentation.
"""

import requests
from bs4 import BeautifulSoup
import pdfplumber
from typing import List, Dict, Tuple, Optional
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
import logging
from difflib import SequenceMatcher
from rapidfuzz import fuzz, process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextSegment:
    """Represents a text segment with its position and semantic info."""
    text: str
    page_number: int
    tag_type: str
    level: Optional[int] = None
    start_pos: int = 0
    end_pos: int = 0

class WikipediaExtractor:
    """Extracts structured markdown from Wikipedia using HTML and PDF."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WikipediaExtractor/1.0)'
        })
    
    def fetch_html(self, url: str) -> BeautifulSoup:
        """Fetch and parse HTML content from Wikipedia URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching HTML: {e}")
            raise
    
    def extract_pdf_text_by_page(self, pdf_path: str) -> List[str]:
        """Extract text from PDF page by page."""
        page_texts = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    page_texts.append(text)
                    logger.info(f"Extracted {len(text)} characters from page {page_num}")
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
        return page_texts
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching."""
        # Remove extra whitespace and normalize unicode
        text = re.sub(r'\s+', ' ', text.strip())
        text = unicodedata.normalize('NFKD', text)
        return text
    
    def extract_semantic_structure(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract semantic structure from Wikipedia HTML."""
        content_div = soup.find('div', {'class': 'mw-parser-output'}) or soup.find('div', {'id': 'mw-content-text'})
        
        if not content_div:
            logger.warning("Could not find main content div")
            return []
        
        elements = []
        
        # Process headings and paragraphs
        for element in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Extract heading
                text = self.normalize_text(element.get_text())
                if text:
                    elements.append({
                        'type': 'heading',
                        'level': int(element.name[1]),
                        'text': text,
                        'raw_text': element.get_text()
                    })
            
            elif element.name == 'p':
                # Extract paragraph
                text = self.normalize_text(element.get_text())
                if text and len(text) > 10:  # Filter out very short paragraphs
                    elements.append({
                        'type': 'paragraph',
                        'text': text,
                        'raw_text': element.get_text()
                    })
            
            elif element.name in ['ul', 'ol']:
                # Extract lists
                items = []
                for li in element.find_all('li', recursive=False):
                    item_text = self.normalize_text(li.get_text())
                    if item_text:
                        items.append(item_text)
                
                if items:
                    elements.append({
                        'type': 'list',
                        'list_type': element.name,
                        'items': items,
                        'text': '\n'.join(items)
                    })
            
            elif element.name == 'table':
                # Extract table content as text
                text = self.normalize_text(element.get_text())
                if text and len(text) > 20:
                    elements.append({
                        'type': 'table',
                        'text': text,
                        'raw_text': element.get_text()
                    })
        
        return elements
    
    def fuzzy_find_text(self, needle: str, haystack: str, threshold: float = 0.6) -> Tuple[int, float]:
        """Find text using fuzzy matching with sliding window."""
        needle = needle.strip()
        if len(needle) < 10:
            return -1, 0.0
        
        best_score = 0.0
        best_pos = -1
        
        # For longer texts, use sliding window approach
        window_size = min(len(needle) + 100, len(haystack))
        step_size = max(20, len(needle) // 4)
        
        for i in range(0, len(haystack) - window_size + 1, step_size):
            window = haystack[i:i + window_size]
            
            # Use different similarity metrics
            ratio = fuzz.partial_ratio(needle, window) / 100.0
            token_ratio = fuzz.token_sort_ratio(needle, window) / 100.0
            
            # Weighted average favoring partial ratio for position finding
            score = (ratio * 0.7 + token_ratio * 0.3)
            
            if score > best_score:
                best_score = score
                best_pos = i
        
        # Also try exact substring matching for high confidence
        if needle[:50] in haystack:
            exact_pos = haystack.find(needle[:50])
            return exact_pos, 1.0
        
        return best_pos if best_score >= threshold else -1, best_score
    
    def find_best_page_match(self, text: str, page_texts: List[str], threshold: float = 0.6) -> Tuple[int, float]:
        """Find the best matching page for given text."""
        best_page = -1
        best_score = 0.0
        
        for page_num, page_text in enumerate(page_texts, 1):
            normalized_page = self.normalize_text(page_text)
            
            # Try different chunk sizes for comparison
            text_chunks = [
                text[:100],  # First 100 chars
                text[:200],  # First 200 chars  
                text,        # Full text
            ]
            
            page_score = 0.0
            for chunk in text_chunks:
                if len(chunk.strip()) < 10:
                    continue
                    
                # Use multiple similarity metrics
                partial_ratio = fuzz.partial_ratio(chunk, normalized_page) / 100.0
                token_ratio = fuzz.token_set_ratio(chunk, normalized_page) / 100.0
                
                # Weight shorter chunks higher for position accuracy
                weight = 1.5 if len(chunk) <= 100 else 1.0
                chunk_score = max(partial_ratio, token_ratio) * weight
                page_score = max(page_score, chunk_score)
            
            if page_score > best_score:
                best_score = page_score
                best_page = page_num
        
        return best_page if best_score >= threshold else -1, best_score
    
    def match_text_to_pages(self, semantic_elements: List[Dict], page_texts: List[str]) -> List[TextSegment]:
        """Match semantic elements to PDF pages using fuzzy matching."""
        segments = []
        match_threshold = 0.6
        
        logger.info(f"Matching {len(semantic_elements)} elements to {len(page_texts)} pages")
        
        # Normalize all page texts
        normalized_pages = [self.normalize_text(page) for page in page_texts]
        
        for i, element in enumerate(semantic_elements):
            text_to_match = self.normalize_text(element['text'])
            
            if len(text_to_match.strip()) < 5:
                continue
                
            # Find best matching page
            best_page, best_score = self.find_best_page_match(
                text_to_match, normalized_pages, match_threshold
            )
            
            if best_page != -1:
                # Find approximate position within the page
                page_text = normalized_pages[best_page - 1]
                pos, pos_score = self.fuzzy_find_text(text_to_match, page_text, 0.5)
                
                segment = TextSegment(
                    text=element['text'],
                    page_number=best_page,
                    tag_type=element['type'],
                    level=element.get('level'),
                    start_pos=pos if pos != -1 else 0,
                    end_pos=pos + len(text_to_match) if pos != -1 else len(text_to_match)
                )
                segments.append(segment)
                
                logger.debug(f"Matched element {i+1}: '{text_to_match[:50]}...' to page {best_page} (score: {best_score:.2f})")
            else:
                logger.warning(f"Could not match element {i+1}: '{text_to_match[:50]}...' (best score: {best_score:.2f})")
        
        logger.info(f"Successfully matched {len(segments)} out of {len(semantic_elements)} elements")
        return segments
    
    def generate_markdown_by_page(self, segments: List[TextSegment]) -> Dict[int, str]:
        """Generate markdown content organized by page."""
        pages_content = {}
        
        # Group segments by page
        pages_segments = {}
        for segment in segments:
            if segment.page_number not in pages_segments:
                pages_segments[segment.page_number] = []
            pages_segments[segment.page_number].append(segment)
        
        # Generate markdown for each page
        for page_num, page_segments in pages_segments.items():
            # Sort segments by position
            page_segments.sort(key=lambda x: x.start_pos)
            
            markdown_lines = []
            markdown_lines.append(f"# Page {page_num}")
            markdown_lines.append("")
            
            for segment in page_segments:
                if segment.tag_type == 'heading':
                    level = segment.level or 2
                    prefix = '#' * min(level + 1, 6)  # +1 because page title is h1
                    markdown_lines.append(f"{prefix} {segment.text}")
                    markdown_lines.append("")
                
                elif segment.tag_type == 'paragraph':
                    markdown_lines.append(segment.text)
                    markdown_lines.append("")
                
                elif segment.tag_type == 'list':
                    # This would need the original element data
                    markdown_lines.append(segment.text)
                    markdown_lines.append("")
                
                elif segment.tag_type == 'table':
                    markdown_lines.append("```")
                    markdown_lines.append(segment.text)
                    markdown_lines.append("```")
                    markdown_lines.append("")
            
            pages_content[page_num] = '\n'.join(markdown_lines)
        
        return pages_content
    
    def save_markdown_pages(self, pages_content: Dict[int, str], output_dir: str):
        """Save markdown content to separate files for each page."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for page_num, content in pages_content.items():
            file_path = output_path / f"page_{page_num:03d}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved page {page_num} to {file_path}")
        
        # Create combined file
        combined_path = output_path / "combined.md"
        with open(combined_path, 'w', encoding='utf-8') as f:
            for page_num in sorted(pages_content.keys()):
                f.write(pages_content[page_num])
                f.write("\n\n---\n\n")  # Page separator
        logger.info(f"Saved combined markdown to {combined_path}")
    
    def process_wikipedia_page(self, url: str, pdf_path: str, output_dir: str = "output"):
        """Main method to process a Wikipedia page."""
        logger.info(f"Processing Wikipedia page: {url}")
        
        # Step 1: Fetch and parse HTML
        soup = self.fetch_html(url)
        logger.info("HTML content fetched and parsed")
        
        # Step 2: Extract semantic structure
        semantic_elements = self.extract_semantic_structure(soup)
        logger.info(f"Extracted {len(semantic_elements)} semantic elements")
        
        # Step 3: Extract PDF text by page
        page_texts = self.extract_pdf_text_by_page(pdf_path)
        logger.info(f"Extracted text from {len(page_texts)} PDF pages")
        
        # Step 4: Match semantic elements to pages
        segments = self.match_text_to_pages(semantic_elements, page_texts)
        logger.info(f"Matched {len(segments)} text segments to pages")
        
        # Step 5: Generate markdown by page
        pages_content = self.generate_markdown_by_page(segments)
        logger.info(f"Generated markdown for {len(pages_content)} pages")
        
        # Step 6: Save results
        self.save_markdown_pages(pages_content, output_dir)
        
        return pages_content


def main():
    """Example usage of the WikipediaExtractor."""
    
    # Configuration
    wikipedia_url = "https://bn.wikipedia.org/wiki/অরুণাচল_প্রদেশ"
    pdf_file_path = "test.pdf"  # Your PDF file path
    output_directory = "wikipedia_output"
    
    # Create extractor and process
    extractor = WikipediaExtractor()
    
    try:
        result = extractor.process_wikipedia_page(
            url=wikipedia_url,
            pdf_path=pdf_file_path,
            output_dir=output_directory
        )
        
        print(f"\nProcessing complete!")
        print(f"Generated markdown for {len(result)} pages")
        print(f"Output saved to: {output_directory}/")
        
        # Show summary of each page
        for page_num, content in result.items():
            lines = content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            print(f"Page {page_num}: {len(non_empty_lines)} lines")
    
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise


# Required dependencies:
# pip install requests beautifulsoup4 pdfplumber rapidfuzz


if __name__ == "__main__":
    main()