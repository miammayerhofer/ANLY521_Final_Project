from pathlib import Path
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import re
import wordninja
import ast


def import_aclu():
    """ Function to import and format the ACLU table """
    aclu_table = pd.read_csv(Path().absolute().parents[0]/Path("modified_data")/"aclu_table_data.csv")
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
    bill_texts = pd.read_csv(Path().absolute().parents[0]/Path("modified_data")/"bill_texts.csv")
    return bill_texts

def import_summaries():
    """ Function to read in the csv file with our bill summaries"""
    summaries = pd.read_csv(Path().absolute().parents[0]/Path("modified_data")/"summaries.csv")
    return summaries

def text_shortener(bill_text):
	"""
	Given a bill text, it finds the section of the PDF where the bill is enacted
	and returns only the text after that
	Enacting bill texts:
	- be it enacted by
	- enact as follows
	- state of [state name] enact
	- assembly of [state name] enact
	"""
	enact_str = r"be it enacted by|enact as follows|state of [a-z]+ enact|assembly of [a-z ]+ enact"
	# Find where the bill is enacted
	if re.search(enact_str, bill_text.lower()):
		enacted_by_index = re.search(enact_str, bill_text.lower()).start() 
	else:
		enacted_by_index = 0
	shortened_str = bill_text[enacted_by_index:]
	# Start at the section
	if "section" in shortened_str.lower():
		first_section_index = re.search("section", shortened_str.lower()).start()
	else:
		first_section_index = 0
	shortened_str = shortened_str[first_section_index:]
	# Remove digits
	shortened_str = re.sub(r' [0-9]+ | [0-9]+[A-Z] ', ' ', shortened_str)
	# List of other strings to remove
	str_to_remove = ['NewTextUnderlinedDELETEDTEXTBRACKETED']
	shortened_str = re.sub('|'.join(str_to_remove), '', shortened_str)
	# Remove section headers
	shortened_str = re.sub('section [0-9]+[a-z] ?', ' ', shortened_str, flags=re.IGNORECASE)
	return shortened_str

def word_ninja_tokenize(string):
	""" Function to tokenize each line of a bill with word ninja """
	# Remove spaces
	stripped = string.replace(' ', '')
	# Use word ninja to infer words
	inferred_words = wordninja.split(string)
	# Join words back together
	cleaned_text = ' '.join(inferred_words)
	return cleaned_text

def merge_data():
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
	data = merge_data()
	# Use word ninja to clean words that might be separated
	data["cleaned_text"] = data["original_text"].apply(lambda x: word_ninja_tokenize(x))
	# Shorten the text
	data["cleaned_text"] = data["cleaned_text"].apply(lambda x: text_shortener(x))
	# Combine state and bill name columns into id column
	data["bill_id"] = data["state"].astype(str) + " " + data["bill_name"].astype(str)
	# Reorder columns
	data = data[["state_name", "state", "bill_id", "bill_name", "keep", "original_text", "cleaned_text", "summary", "summary_source", "category", "status", "link"]]
	# Make a csv of all the data
	data.to_csv(Path().absolute().parents[0]/Path("modified_data")/"text_and_summaries_all.csv", index = False)
	# Remove columns without text or summary
	filtered_data = data[data["summary"] == 1]
	# Make a csv of the filtered data
	filtered_data.to_csv(Path().absolute().parents[0]/Path("modified_data")/"text_and_summaries_filtered.csv", index = False)
