import pandas as pd
import wikipedia
import time

# Define the input and output file names
input_file = 'original_csvs/india_tourism.csv'
output_file = 'domain-csvs/tourism.csv'

# Read the keywords from the CSV file
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found.")
    exit()

# Ensure the 'keywords' column exists
if 'Keyword' not in df.columns:
    print("Error: The CSV file must contain a column named 'Keyword'.")
    exit()

# Initialize a list to store the results
results = []
first_links = []
second_links = []
third_links = []

for index, row in df.iterrows():
    search_term = str(row['Keyword'])
    try:
        # Search Wikipedia for the keyword and get the first result's page object
        page = wikipedia.page(search_term, auto_suggest=False, redirect=True)
        link = page.url
        first_links.append(link)
        second_links.append("")
        third_links.append("")

        print(f"Found link for '{search_term}': {link}")
    except wikipedia.exceptions.PageError:
        suggestions = wikipedia.search(search_term)
        first_suggestion = suggestions[0]
        print(f"No page found for '{search_term}'. Searching instead")
        print(f"First suggestion: {first_suggestion}")
        try:
            suggested_page = wikipedia.page(first_suggestion, auto_suggest=False, redirect=True)
            first_links.append(suggested_page.url)
            second_links.append("")
            third_links.append("")
        except Exception as e:
            print("Error again")
            first_links.append("")
            second_links.append("")
            third_links.append("")
        
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation errors by taking the first suggestion
        try:
            # Take the first option from the disambiguation list
            first_option = e.options[0]
            page = wikipedia.page(first_option, auto_suggest=False, redirect=True)
            link = page.url
            first_links.append(link)
            if len(e.options) > 2:
                try:
                    time.sleep(0.5)
                    second_option = e.options[1]
                    page1 = wikipedia.page(second_option, auto_suggest=False, redirect=True)
                    time.sleep(0.5)
                    third_option = e.options[2]
                    page2 = wikipedia.page(third_option, auto_suggest=False, redirect=True)

                    second_links.append(page1.url)
                    third_links.append(page2.url)

                except wikipedia.DisambiguationError as e2:
                    second_links.append("")
                    third_links.append("")
                except (wikipedia.exceptions.PageError, IndexError):
                    second_links.append("")
                    third_links.append("")
                    
            else:
                try:
                    time.sleep(0.5)
                    second_option = e.options[1]
                    page = wikipedia.page(second_option, auto_suggest=False, redirect=True)
                    second_links.append(page.url)
                except wikipedia.DisambiguationError as e2:
                    second_links.append("")
                except (wikipedia.exceptions.PageError, IndexError):
                    second_links.append("")
                

                third_links.append("")
            
            print(f"Disambiguation resolved for '{search_term}', using '{first_option}': {link}")
        except (wikipedia.exceptions.PageError, IndexError):
            first_links.append("")
            second_links.append("")
            third_links.append("")
            print(f"Could not resolve disambiguation for '{search_term}'")
        except wikipedia.exceptions.DisambiguationError as e:
            print("Double Disambiguation. SKipping")
            first_links.append("")
            second_links.append("")
            third_links.append("")
    except Exception as e:
        # Catch any other unexpected errors
        first_links.append("")
        second_links.append("")
        third_links.append("")
        print(f"An unexpected error occurred for '{search_term}': {e}")

    time.sleep(0.5)

print(len(first_links), len(second_links), len(third_links))

df['wikipedia_link'] = first_links
df['secondary_wiki_link'] = second_links
df['tertiary_wiki_link'] = third_links

df.to_csv(output_file, index=False)

print(f"\nProcessing complete. The results have been saved to '{output_file}'.")
    



# Iterate over each keyword in the DataFrame
# for keyword in df['Keyword']:
#     # Convert the keyword to a string to handle potential non-string types
#     search_term = str(keyword)

#     try:
#         # Search Wikipedia for the keyword and get the first result's page object
#         page = wikipedia.page(search_term, auto_suggest=False, redirect=True)
#         link = page.url
#         print(f"Found link for '{search_term}': {link}")
#     except wikipedia.exceptions.PageError:
#         # Handle cases where the keyword doesn't match any Wikipedia page
#         link = "No page found"
#         print(f"No page found for '{search_term}'")
#     except wikipedia.exceptions.DisambiguationError as e:
#         # Handle disambiguation errors by taking the first suggestion
#         try:
#             # Take the first option from the disambiguation list
#             first_option = e.options[0]
#             page = wikipedia.page(first_option, auto_suggest=False, redirect=True)
#             link = page.url
#             print(f"Disambiguation resolved for '{search_term}', using '{first_option}': {link}")
#         except (wikipedia.exceptions.PageError, IndexError):
#             link = "Disambiguation error"
#             print(f"Could not resolve disambiguation for '{search_term}'")
#     except Exception as e:
#         # Catch any other unexpected errors
#         link = "Error"
#         print(f"An unexpected error occurred for '{search_term}': {e}")
    
    # Append the keyword and its corresponding link to our results list
    # results.append({'keyword': search_term, 'wikipedia_link': link})
    # time.sleep(0.5)

# Create a new DataFrame from the results list
# results_df = pd.DataFrame(results)

# Save the new DataFrame to a CSV file
