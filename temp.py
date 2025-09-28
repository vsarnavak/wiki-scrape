import os

def add_prefix_to_file(filepath: str, prefix: str):
    try:
        # Step 1: Read all lines from the file
        with open(filepath, 'r', encoding = 'utf-8') as file:
            lines = file.readlines()
        modified_lines = [f"{prefix}{line}" for line in lines]
        with open(filepath, 'w', encoding = 'utf-8') as file:
            file.writelines(modified_lines)
        print(f"Successfully added the prefix to all lines in '{filepath}'.")

    except FileNotFoundError:
        print(f"Error: The file at '{filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    filepath = 'dumps/tewiki-latest-all-titles-in-ns0.txt'
    my_prefix = 'https://te.wikipedia.org/wiki/'

    # Call the function to add the prefix to the file.
    add_prefix_to_file(filepath, my_prefix)
