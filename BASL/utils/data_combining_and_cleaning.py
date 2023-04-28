import logging
import time
import argparse
import os
import pandas as pd

from math import log
from bill_text_cleaner_splitter import BillTextCleaner, BillTextSplitter

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

def import_aclu():
    """ Function to import and format the ACLU table """
    aclu_table = pd.read_csv("../modified_data/aclu_table_data.csv")
    # Remove spaces and periods in bill names
    aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(" ", "", regex = False)
    aclu_table["bill_name"] = aclu_table["bill_name"].str.replace(".", "", regex = False)
    # Dictionary for mapping state names to acronyms
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
    return aclu_table

def import_bill_texts():
    """ Function to read in the csv file with our bill summaries"""
    bill_texts = pd.read_csv("../modified_data/bill_texts.csv")
    return bill_texts

def import_summaries():
    """ Function to read in the csv file with our bill summaries"""
    summaries = pd.read_csv("../modified_data/summaries.csv")
    return summaries

def merge_data():
    """
	Function to merge the aclu, summary, and bill data into one data frame
	"""
	# Get the bill text
    bill_text_data = import_bill_texts()
    # Get the ACLU table
    aclu_table = import_aclu()
    # Get our bill summaries
    summary_data = import_summaries()
    # Merge data frames
    merge1 = aclu_table.merge(bill_text_data, on = ["state", "bill_name"])
    merge_all = merge1.merge(summary_data, on = ["state", "bill_name"])
	# Clean up data frame
    merge_all = merge_all.drop("full_state_y", axis = 1)
    merge_all = merge_all.rename(columns = {"full_state_x": "state_name", "text": "original_text", "source": "summary_source"})
    return merge_all


if __name__ == "__main__":

    startTime = time.time()
    timeTag = time.strftime('%Y%m%d_%H_%M_%S')

    # Read arguments
    parser = argparse.ArgumentParser(description = "Code to combine all of the data, clean it, and split it.")
    parser.add_argument("-o", "--outdir", required = True, help = "Path to logging")
    args = parser.parse_args()

    # Begin logger
    logger = setup_logger(f"log_{timeTag}.log", args.outdir)
    logger.info("Running data combining and cleaning script.")
    logger.info(f"Output directory: {args.outdir}")

    # Merge the data
    logger.info("Merging the data into one data frame and filtering.")
    data = merge_data()
    # Combine state and bill name columns into id column and remove columns without text or summary
    data["bill_id"] = data["state"].astype(str) + " " + data["bill_name"].astype(str)
    filtered_data = data[data["keep"] == 1]

    # Log the current filtered data
    logger.info(f"\n{filtered_data}")

	# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability)
    words = open("../modified_data/our_words.txt").read().split()
    wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
    maxword = max(len(x) for x in words)

    # Clean and split all bill text
    logger.info("Cleaning and splitting all of the bill text.")
    filtered_data["cleaned_text"] = filtered_data["original_text"].apply(lambda x: BillTextCleaner(x, wordcost, maxword).get_clean_text())
    filtered_data["split_cleaned_text"] = filtered_data["cleaned_text"].apply(lambda x: BillTextSplitter(x).get_split_text())
    filtered_data = filtered_data[["state_name", "state", "bill_id", "bill_name", "original_text", \
                                    "cleaned_text", "split_cleaned_text", "summary", "summary_source", \
                                    "category", "status", "link"]]
    # Log the current filtered data
    logger.info(f"\n{filtered_data}")
	# Make a csv of the filtered data
    filtered_data.to_csv("../modified_data/text_and_summaries_filtered.csv", index = False)
