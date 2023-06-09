import os
import re
import zlib
import logging
import time
import argparse
import pandas as pd
from pathlib import Path

from PyPDF2 import PdfReader

def setup_logger(log_file_name, log_dir_path):
    """ Function for logging this script """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_file_path = os.path.join(log_dir_path, log_file_name)
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def read_files():
    """ Funciton to read in the bill PDFs and scrape the text """
    # Set the initial starting path for the bill pdfs and go through each
    # depending where this script is used it will navigate to find the /raw_data folder differently
    path_parts = Path().absolute().parts
    if Path().absolute().name == 'BASL':
        path = Path().absolute()/"raw_data"
    elif path_parts[len(path_parts)-2] == 'BASL':
        path = Path().absolute().parents[0]/"raw_data"
    bill_states, bill_names, bill_texts = [], [], []
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
    # Make a dictionary and convert to a data frame
    bills_dict = {"state": bill_states, "bill_name": bill_names, "text": bill_texts}
    bills_df = pd.DataFrame(bills_dict)
    # Sort bills in order by state
    bills_df = bills_df.sort_values("state").reset_index(drop = True)
    bills_df = bills_df.reset_index(drop = True)
    return bills_df


def scrape_text(path, file_name):
    """ Given a PDF's file name, returns the raw text of that file """
    # Open the current PDF file
    pdf = open(os.path.join(path, file_name), "rb")
    full_page_text = ''
    # If this PDF is a texas file, we need to use FlateDecode to decode the file
    if file_name.startswith("tx"):
        stream = re.compile(rb'.*?FlateDecode.*?stream(.*?)endstream', re.S)
        # Stream in the data
        for s in stream.findall(pdf.read()):
            s = s.strip(b'\r\n')
            try:
                # Decompress the file into bytes and then decode into regular text
                word_string = zlib.decompress(s)
                word_string = word_string.decode('utf-8')
                word_string = word_string.split("\n")
                # The actual text is enclosed in parentheses
                page_text = [re.sub('\(|\)', '', re.search("\((.*)\)", i).group(0)) for i in word_string if i.startswith("(")]
                # Remove numbers
                page_text = [i for i in page_text if not i.isdigit()]
                page_text = ' '.join(page_text)
                # Remove extra spaces
                page_text = re.sub(r'\n|  ', ' ', page_text)
                # Append to the full string
                full_page_text += page_text
            except Exception as e:
                pass
    # If this PDF is not a texas file, read it in with the Python PDF reader
    # Source code: https://gist.github.com/averagesecurityguy/ba8d9ed3c59c1deffbd1390dafa5a3c2
    else:
        # Create a PDF reader object
        pdf_reader = PdfReader(pdf)
        # Loop through each page in the PDF document
        for page_number in range(len(pdf_reader.pages)):
            # Extract the text from the current page
            page_text = pdf_reader.pages[page_number].extract_text()
            # Remove new lines
            page_text = re.sub(r'\n', ' ', page_text)
            # Getting rid of non-ascii characters
            page_text = re.sub(r"â??", "", page_text)
            page_text = page_text.encode('ascii', 'ignore').decode('ascii')
            page_text = re.sub(r'[^\x00-\x7F]+', " ", page_text)
            page_text = re.sub(r'[^a-zA-Z0-9]', " ", page_text)
            full_page_text += page_text
        # Close the PDF file
        pdf.close()
    return full_page_text


if __name__ == "__main__":

    startTime = time.time()
    timeTag = time.strftime('%Y%m%d_%H_%M_%S')

    # Read arguments
    parser = argparse.ArgumentParser(description = "Code to scrape the bill text from each of their PDFs")
    parser.add_argument("-o", "--outdir", required = True, help = "Path to logging")
    args = parser.parse_args()

    # Begin logger
    logger = setup_logger(f"log_{timeTag}.log", args.outdir)
    logger.info("Running bill text scraper script.")
    logger.info(f"Output directory: {args.outdir}")

    # Read in the pdfs and make a csv file to store them
    logger.info("Getting all of the bill text into a data frame.")
    bills_df = read_files()
    logger.info(f"\n{bills_df}")
    bills_df.to_csv("../modified_data/bill_texts.csv", index = False)





