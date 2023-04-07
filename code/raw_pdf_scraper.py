# ==============================
# Scrapes the pdfs collected in 
# raw_data folder
# Filename: raw_pdf_scraper.py
# Author: Mia Mayerhofer
# ==============================

# IMPORT REQUIRED PACKAGES
from PyPDF2 import PdfReader
import os
import pandas as pd
import re
import zlib


def read_files():
    # Set the initial starting path for the bill pdfs
    path = "../raw_data/"
    # Store bill names and texts lists
    bill_states, bill_names, bill_texts = [], [], []
    # go through all the files
    for filename in os.listdir(path):
        # Prep for opening the PDF
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            full_bill_text = scrape_text(path, filename_lower)
            # Add full bill text to list
            bill_texts.append(full_bill_text)
            # Get the bill name and state and append to lists
            filename_split1 = filename.split("_")
            # Add state to state list
            bill_states.append(filename_split1[0])
            # Add bill names to list
            filename_split2 = filename_split1[1].split(".")
            bill_names.append(filename_split2[0])
            
    print("bill states", len(bill_states))
    print("bill names", len(bill_names))
    print("bill texts", len(bill_texts))
    # Make a dictionary
    bills_dict = {"state": bill_states, "bill_name": bill_names, "text": bill_texts}
    # Convert to data frame
    bills_df = pd.DataFrame(bills_dict)
    # Sort bills in order by state
    bills_df = bills_df.sort_values("state").reset_index(drop = True)
    bills_df = bills_df.reset_index(drop = True)
    # Make a csv file
    bills_df.to_csv("../modified_data/bill_texts_full_text.csv", index=False)
    return bills_df



"""
Given a PDF's file name, returns the raw text of that file
"""
def scrape_text(path, file_name):
    print(file_name)
    # Open the current PDF file
    pdf = open(os.path.join(path, file_name), "rb")
    # Make an empty string to get the full text
    full_page_text = ''
    # if this PDF is a texas file, we need to use FlateDecode to decode the file
    if file_name.startswith("tx"):
        stream = re.compile(rb'.*?FlateDecode.*?stream(.*?)endstream', re.S)
        # stream in the data
        for s in stream.findall(pdf.read()):
            s = s.strip(b'\r\n')
            try:
                # decompress the file into bytes and then decode into regular text
                word_string = zlib.decompress(s)
                word_string = word_string.decode('utf-8')
                word_string = word_string.split("\n")
                # the actual text is enclosed in parentheses
                page_text = [re.sub('\(|\)', '', re.search("\((.*)\)", i).group(0)) for i in word_string if i.startswith("(")]
                # remove numbers
                page_text = [i for i in page_text if not i.isdigit()]
                page_text = ' '.join(page_text)
                # remove extra spaces
                page_text = re.sub(r'\n|  ', ' ', page_text)
                # print(page_text)
                # append to the full string
                full_page_text += page_text
            except Exception as e:
                pass
                # print(e)
        # print(full_page_text)
    # if this PDF is not a texas file, read it in with the Python PDF reader
    # source code: https://gist.github.com/averagesecurityguy/ba8d9ed3c59c1deffbd1390dafa5a3c2
    else:
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf)
        # Loop through each page in the PDF document
        for page_number in range(len(pdf_reader.pages)):
            # Extract the text from the current page
            page_text = pdf_reader.pages[page_number].extract_text()

            # remove new lines
            page_text = re.sub(r'\n', ' ', page_text)

            # Getting rid of non-ascii characters
            page_text = re.sub(r"â??", "", page_text)
            page_text = page_text.encode('ascii', 'ignore').decode('ascii')
            page_text = re.sub(r'[^\x00-\x7F]+', " ", page_text)
            page_text = re.sub(r'[^a-zA-Z0-9]', " ", page_text)
            full_page_text += page_text
            # print(page_text[:200])
        # Close the PDF file
        pdf.close()
    return full_page_text


def import_aclu():
    # Import ACLU table
    aclu_table = pd.read_csv("../modified_data/aclu_bill_data.csv")
    # Remove space in bill names
    aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(" ", "", regex = False)
    aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(".", "", regex = False)
    # Create a dictionary mapping state names to acronyms
    state_dict = {
        'Alabama': 'AL', 'Alaska': 'AK','Arizona': 'AZ','Arkansas': 'AR',
        'California': 'CA','Colorado': 'CO','Connecticut': 'CT','Delaware': 'DE',
        'Florida': 'FL','Georgia': 'GA','Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL','Indiana': 'IN',
        'Iowa': 'IA','Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA','Maine': 'ME','Maryland': 'MD',
        'Massachusetts': 'MA','Michigan': 'MI','Minnesota': 'MN','Mississippi': 'MS','Missouri': 'MO',
        'Montana': 'MT','Nebraska': 'NE','Nevada': 'NV','New Hampshire': 'NH','New Jersey': 'NJ',
        'New Mexico': 'NM','New York': 'NY','North Carolina': 'NC','North Dakota': 'ND','Ohio': 'OH',
        'Oklahoma': 'OK','Oregon': 'OR','Pennsylvania': 'PA','Rhode Island': 'RI','South Carolina': 'SC',
        'South Dakota': 'SD','Tennessee': 'TN','Texas': 'TX','Utah': 'UT','Vermont': 'VT','Virginia': 'VA',
        'Washington': 'WA','West Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY'}
    # Change state names to acronym
    aclu_table = aclu_table.rename(columns = {"state": "full_state"})
    aclu_table["state"] = aclu_table["full_state"].map(state_dict)
    aclu_table.loc[211, "bill_name"] = "SB228"
    return aclu_table

def merge_data():
    bills_df = read_files()
    aclu_table = import_aclu()
    # Get the bills that are different between the two data frames
    #list(set(bills_df.bill_name) - set(aclu_table.bill_name))
    #list(set(aclu_table.bill_name) - set(bills_df.bill_name))

    # Merge data frames
    merged_df = aclu_table.merge(bills_df, on = ["state", "bill_name"])

    # Make a csv file
    merged_df.to_csv("../modified_data/merged_bill_data_full_text.csv", index=False)


if __name__ == "__main__":
    merge_data()





