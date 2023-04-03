# =========================
# Combining ACLU csv files
# File: bill_merger.ipynb
# Author: Mia Mayerhofer
# =========================

# IMPORT PACKAGES
import pandas as pd
import re

# MAKE A FUNCTION TO EXTRACT STATE AND NAMES FROM BILL_TEXTS.CSV'S NAME COLUMN
def state_and_name_extractor(string):
    # Split on underscore
    split_string = string.split("_")
    # Get the state acronym
    state_acronym = split_string[0]
    # Extract the bill's number
    bill_number = re.findall(r'\d+', split_string[1])
    bill_number = str(bill_number[0]).lstrip('0')
    # Get the type of bill
    no_nums = re.sub(r'\d+', '', split_string[1])
    # Remove last letter if more than two bc bill types are either 1 or 2 characters
    if len(no_nums) > 2:
        bill_type = no_nums[:-1]
    else: bill_type = no_nums
    # Return necessary info
    return state_acronym, bill_number, bill_type


# IMPORT DATA
aclu_table = pd.read_csv("../modified_data/aclu_bill_data.csv")
bill_texts = pd.read_csv("../modified_data/bill_texts.csv", encoding='iso-8859-1')
# Drop unamed column
bill_texts = bill_texts.drop(bill_texts.columns[0], axis = 1)

# PREP BILL_TEXTS FOR MERGE
# Make new columns
bill_texts["state_acronym"] = ""
bill_texts["bill_number"] = ""
bill_texts["bill_type"] = ""
for i in range(len(bill_texts.name)):
    # Put into extraction function to get the state, number, and type for each bill and add as new columns
    bill_texts.state_acronym[i], bill_texts.bill_number[i], bill_texts.bill_type[i] = state_and_name_extractor(bill_texts.name[i])

# FORMAT ACLU_BILL_DATA TABLE FOR MERGE
aclu_table["bill_number"] = ""
aclu_table["bill_type"] = ""
for i in range(len(aclu_table.bill_name)):
    # Split on space to separate bill type from number
    split_string = aclu_table.bill_name[i].split(" ")
    aclu_table.bill_type[i] = split_string[0]
    aclu_table.bill_number[i] = split_string[1]

# MERGE
merged_df = pd.merge(aclu_table, bill_texts, on = ["bill_number", "bill_type"])
# Drop unecessary columns
merged_df = merged_df.drop(columns=["name"])
# Rearrange columns
merged_df = merged_df[["state", "state_acronym", "bill_name", "bill_type", "bill_number", "category", "link", "status", "text"]]
# Add as a csv file
merged_df.to_csv("../modified_data/merged_bill_data.csv")


