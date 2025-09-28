from bs4 import BeautifulSoup

with open('test.html', 'r', encoding='utf-8') as f:
    html_doc = f.read()

# The text we are searching for
text_to_find = "Land of Dawn-Lit Mountains" # Printed, not perfect :অরুণাচল প্রদেশ

# Create a BeautifulSoup object
soup = BeautifulSoup(html_doc, 'html.parser')

# Find the parent container that holds the text
# parent_div = soup.find()
text = soup.get_text()
text = text.split()
text = ' '.join(text)
# print(text)
# Check if the text exists within the parent container
if text and text_to_find in text:
    print(f"Text found in the 'article-body' div!")
    
    # Optional: Find the specific divs that contain parts of the text
    # You would need to iterate through the child elements and check their content
    
    print("Finding individual divs containing parts of the text:")
    for child in soup.find_all():
        if text_to_find.split()[0] in child.get_text(): # Check for the first word
            print(f"Found part of the text in: {child.prettify()}")

else:
    print("Text not found.")