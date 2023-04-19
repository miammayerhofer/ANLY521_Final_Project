import pandas as pd
import re
import wordninja
from math import log


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

def text_shortener(bill_text):
	"""
	This function performs several operations to shorten the bill texts:
		- only begin bill on a phrase that marks the start of the bill text (e.g. 'be enacted by...')
		- remove section headers
		- remove odd patterns
		- remove sections of multiple spaces
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
	# Remove all instances of more than 1 space
	shortened_str = re.sub(r'\s{2,}', ' ', shortened_str)
    # Common phrase among bill to remove
	shortened_str = re.sub(r'NewTextUnderlinedDELETEDTEXTBRACKETED', ' ', shortened_str, flags = re.IGNORECASE)
	shortened_str = re.sub(r'New Text Underlined DELETED TEXT BRACKETED', ' ', shortened_str, flags = re.IGNORECASE)
	# Remove section headers
	shortened_str = re.sub(r'sec \w+ ', ' ', shortened_str, flags = re.IGNORECASE)
	shortened_str = re.sub(r'section \w+ ', ' ', shortened_str, flags = re.IGNORECASE)
	# Remove strange section header pattern noticed in a few bills
	shortened_str = re.sub(r'\\[A-Za-z]+\b', ' ', shortened_str, flags = re.IGNORECASE)
	# Remove digits and strings of digits
	shortened_str = re.sub(r' [0-9]+ | [0-9]+[A-Z] ', ' ', shortened_str)
	shortened_str = re.sub(r'\b\d+\b', ' ', shortened_str)
	# Remove any patterns of multiple capital letters separated by spaces: "A A A"
	shortened_str = re.sub(r'\b[A-Z](?:\s+[A-Z])+\b', ' ', shortened_str)
	shortened_str = re.sub(r'\d+', ' ', shortened_str)
	# Remove all instances of more than 1 space
	shortened_str = re.sub(r'\s{2,}', ' ', shortened_str)
	return shortened_str.strip()

def infer_spaces(bill_text, wordcost, maxword):
	"""Uses dynamic programming to infer the location of spaces in a string without spaces - basis of wordninja code
	Source code: https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words
	"""
	# Prepare string (lower and remove all spaces)
	s = bill_text.lower()
	s = re.sub(r'\s+', "", s)
	def best_match(i):
		"""
		Find the best match for the i first characters, assuming cost has been built for the i-1 first characters
		Returns a pair (match_cost, match_length)
		"""
		candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
		return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)
	# Build cost array
	cost = [0]
	for i in range(1,len(s)+1):
		c,k = best_match(i)
		cost.append(c)
    # Backtrack to recover the minimal-cost string
	out = []
	i = len(s)
	while i>0:
		c,k = best_match(i)
		assert c == cost[i]
		out.append(s[i-k:i])
		i -= k
	return " ".join(reversed(out))

def word_ninja_tokenize(string):
	""" Function to tokenize each line of a bill with word ninja """
	# Remove spaces
	stripped = string.replace(' ', '')
	# Use word ninja to infer words
	inferred_words = wordninja.split(stripped)
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
	# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability)
	words = open("../../modified_data/words-by-frequency.txt").read().split()
	wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
	maxword = max(len(x) for x in words)
	# Use word ninja to clean words that might be separated and shorten the text
	data["cleaned_text"] = data["original_text"].apply(lambda x: text_shortener(x))
	data["cleaned_text"] = data["cleaned_text"].apply(lambda x: infer_spaces(x, wordcost, maxword))
	# Combine state and bill name columns into id column
	data["bill_id"] = data["state"].astype(str) + " " + data["bill_name"].astype(str)
	# Reorder columns
	data = data[["state_name", "state", "bill_id", "bill_name", "keep", "original_text", "cleaned_text", "summary", "summary_source", "category", "status", "link"]]
	# Make a csv of all the data
	data.to_csv("../../modified_data/text_and_summaries_all.csv", index = False)
	# Remove columns without text or summary
	filtered_data = data[data["keep"] == 1]
	# Make a csv of the filtered data
	filtered_data.to_csv("../../modified_data/text_and_summaries_filtered.csv", index = False)
