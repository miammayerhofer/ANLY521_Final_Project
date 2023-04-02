# ======================
# Bill Text Extraction 
# File: bill_pdf_scraper.py
# Author: Mia Mayerhofer
# ======================

## IMPORT REQUIRED PACKAGES
from PyPDF2 import PdfReader
import os
import pandas as pd
import re


## READ IN THE PDF TEXT

# Store bill names and texts lists
bill_names, bill_texts = [], []
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
        curr_text = []
        full_string = ""
        # Loop through each page in the PDF document
        for page in range(pdf_reader.getNumPages()):
            # Extract the text from the current page
            page_text = pdf_reader.getPage(page).extractText()
            # Add current page text to list
            curr_text.append(page_text)
            full_string = full_string + page_text
        # Add full text to list
        full_text = full_string.replace("\n", " ").replace("â??", " ")
        # Getting rid of non-ascii characters
        full_text = full_text.encode('ascii', 'ignore').decode('ascii')
        full_text = re.sub(r'[^\x00-\x7F]+', " ", full_text)
        full_text = re.sub(r'[^a-zA-Z0-9]', " ", full_text)
        bill_texts.append(full_text)
        # Get the bill name and append to list
        filename_list = filename.split(".")
        bill_names.append(filename_list[0])
        # Close the PDF file
        pdf.close()
# Make a dictionary
bills_dict = {"name": bill_names, "text": bill_texts}
# Convert to data frame
bills_df = pd.DataFrame(bills_dict)
bills_df["text"] = bills_df["text"].astype(str)
# Make a csv file
bills_df.to_csv("../modified_data/bill_texts.csv")


