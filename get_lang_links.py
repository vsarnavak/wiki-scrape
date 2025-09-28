import pandas as pd
import csv
import os

def extract_href_before_lang(html_content: str, lang_code: str) -> str | None:
    # 1. Find first occurrence of lang="{lang_code}"
    lang_str = f'lang="{lang_code}"'
    lang_pos = html_content.find(lang_str)
    if lang_pos == -1:
        return None  # not found

    # 2. Move backwards to find the last 'href="' before that point
    href_pos = html_content.rfind('href="', 0, lang_pos)
    if href_pos == -1:
        return None

    # 3. Extract the URL
    start = href_pos + len('href="')
    end = html_content.find('"', start)
    if end == -1:
        return None

    return html_content[start:end]

domain = 'politics'
# df = pd.read_csv('wikipedia_links_geo.csv')
input_file = f'domain-csvs/{domain}.csv'
output_file = f'domain-csvs/{domain}.csv'

df_ = pd.read_csv(input_file)
# links = df['link']

lang_codes = ["as", "bn", "gu", "hi", "kn", "ml", "mr", "or", "ta", "te"]
lang_dict = {"as" : 0, "bn" : 0, "gu" : 0, "hi" : 0, "kn" : 0, "ml" : 0, "mr" : 0, "or" : 0, "ta" : 0, "te" : 0}
links_dict = {"as" : [], "bn" : [], "gu" : [], "hi" : [], "kn" : [], "ml" : [], "mr" : [], "or" : [], "ta" : [], "te" : []}
lang_counts = []

for index,row in df_.iterrows():
    count = 0
    if not pd.isna(row['wikipedia_link']):
        html_name = row['Keyword']
        with open(f"html_files/{domain}/{html_name}.html", 'r', encoding='utf-8') as f:
            html_data = f.read()
        for lang_code in lang_codes:
            lang_link = extract_href_before_lang(html_data, lang_code)  
            if lang_link is not None:
                links_dict[lang_code].append(lang_link)
                lang_dict[lang_code] += 1
                count += 1
            else:
                links_dict[lang_code].append("")
        lang_counts.append(count)
    else:
        for lang_code in lang_codes:
            links_dict[lang_code].append("")
        lang_counts.append(0)

df_['language_count'] = lang_counts

for lang_code in lang_codes:
    df_[lang_code] = lang_code
    df_[f"{lang_code}_wiki_link"] = links_dict[lang_code]

# for html_file in os.listdir('html_files/geography'):
#     with open(f"html_files_geo/{html_file}", 'r', encoding='utf-8') as f:
#         html_data = f.read()
#     for lang_code in lang_codes:
#         lang_link = extract_href_before_lang(html_data, lang_code)  
    
df_.to_csv(output_file, index = False)
print(lang_dict)
