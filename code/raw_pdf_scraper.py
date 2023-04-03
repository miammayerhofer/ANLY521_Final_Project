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


# Store bill names and texts lists
bill_states, bill_names, bill_texts = [], [], []
# Set the initial starting path for the bill pdfs
path = "../raw_data/"
for filename in os.listdir(path):
    # Prep for opening the PDF
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        # Open the current PDF file
        pdf = open(os.path.join(path, filename), "rb")
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf)
        # Make a list to store the text from each page in
        curr_lines = []
        # Loop through each page in the PDF document
        for page in range(pdf_reader.getNumPages()):
            # Extract the text from the current page
            page_text = pdf_reader.getPage(page).extractText()
            if filename == "AK_HB27.pdf":
                print("PAGE TEXT:", page_text)
                print("SPLIT LINES:", page_text.splitlines())
            split_lines = page_text.splitlines()
            for i in range(len(split_lines)):
                # Getting rid of non-ascii characters
                split_lines[i] = split_lines[i].replace("â??", "")
                split_lines[i] = split_lines[i].encode('ascii', 'ignore').decode('ascii')
                split_lines[i] = re.sub(r'[^\x00-\x7F]+', "", split_lines[i])
                split_lines[i] = re.sub(r'[^a-zA-Z0-9]', "", split_lines[i])
            # Add lines to list
            curr_lines += split_lines
        # Add full bill text to list
        bill_texts.append(curr_lines)
        # Get the bill name and state and append to lists
        filename_split1 = filename.split("_")
        # Add state to state list
        bill_states.append(filename_split1[0])
        # Add bill names to list
        filename_split2 = filename_split1[1].split(".")
        bill_names.append(filename_split2[0])
        # Close the PDF file
        pdf.close()
# Make a dictionary
bills_dict = {"state": bill_states, "bill_name": bill_names, "text": bill_texts}
# Convert to data frame
bills_df = pd.DataFrame(bills_dict)
# Sort bills in order by state
bills_df = bills_df.sort_values("state").reset_index(drop = True)
bills_df = bills_df.reset_index(drop = True)
# Make a csv file
bills_df.to_csv("../modified_data/bill_texts.csv")


# Import ACLU table
aclu_table = pd.read_csv("../modified_data/aclu_bill_data.csv")
# Remove space in bill names
aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(" ", "")
aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(".", "")
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
aclu_table["state"] = aclu_table["state"].map(state_dict)
aclu_table.loc[211, "bill_name"] = "SB228"

# Get the bills that are different between the two data frames
#list(set(bills_df.bill_name) - set(aclu_table.bill_name))
#list(set(aclu_table.bill_name) - set(bills_df.bill_name))

# Merge data frames
merged_df = aclu_table.merge(bills_df, on = ["state", "bill_name"])

# Make a csv file
merged_df.to_csv("../modified_data/merged_bill_data.csv")


