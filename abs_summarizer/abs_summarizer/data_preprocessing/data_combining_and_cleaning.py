import pandas as pd

from math import log
from abs_summarizer.util.bill_text_cleaner_splitter import BillTextCleaner, BillTextSplitter

def import_aclu():
    """ Function to import and format the ACLU table """
    aclu_table = pd.read_csv("../../modified_data/aclu_table_data.csv")
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
    bill_texts = pd.read_csv("../../modified_data/bill_texts.csv")
    return bill_texts

def import_summaries():
    """ Function to read in the csv file with our bill summaries"""
    summaries = pd.read_csv("../../modified_data/summaries.csv")
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
    # Merge the data
    data = merge_data()

    # Combine state and bill name columns into id column
    data["bill_id"] = data["state"].astype(str) + " " + data["bill_name"].astype(str)
    # Remove columns without text or summary
    filtered_data = data[data["keep"] == 1]

	# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability)
    words = open("../../modified_data/our_words.txt").read().split()
    wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
    maxword = max(len(x) for x in words)

    # Clean and split all bill text
    filtered_data["cleaned_text"] = filtered_data["original_text"].apply(lambda x: BillTextCleaner(x, wordcost, maxword).get_clean_text())
    filtered_data["split_cleaned_text"] = filtered_data["cleaned_text"].apply(lambda x: BillTextSplitter(x).get_split_text())

	# Reorder columns
    filtered_data = filtered_data[["state_name", "state", "bill_id", "bill_name", "original_text", \
                                    "cleaned_text", "split_cleaned_text", "summary", "summary_source", \
                                    "category", "status", "link"]]
	# Make a csv of the filtered data
    filtered_data.to_csv("../../modified_data/text_and_summaries_filtered.csv", index = False)
