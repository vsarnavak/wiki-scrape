# General
main.py has the main code to make PDF files from wikipedia pages by taking a link, injecting some CSS, use local font files to change the font, and use Chromium's PDF renderer to render the pdf.

We are making multi-column layouts and using various fonts to have as much variety as possible for training models.


master.csv contains a set of 1662 topics related to India where we have taken the english pages, then added the links of the same pages in other languages if it exists.
