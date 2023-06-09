import pandas as pd
import re
from math import log
from transformers import AutoTokenizer, pipeline
import numpy as np
import argparse
import logging
import time
import os

def setup_logger(log_file_name, log_dir_path):
	'''Function to initialize logger'''
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	log_file_path = os.path.join(log_dir_path, log_file_name)
	file_handler = logging.FileHandler(log_file_path)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger

def import_aclu(indir):
    """ Function to import and format the ACLU table """
    aclu_table = pd.read_csv(os.path.join(indir, "aclu_table_data.csv")) #"../../modified_data/aclu_table_data.csv"
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

def import_bill_texts(indir):
    """ Function to read in the csv file with our bill summaries"""
    bill_texts = pd.read_csv(os.path.join(indir, "bill_texts.csv")) #"../../modified_data/bill_texts.csv"
    return bill_texts

def import_summaries(indir):
    """ Function to read in the csv file with our bill summaries"""
    summaries = pd.read_csv(os.path.join(indir, "summaries.csv")) #"../../modified_data/summaries.csv"
    return summaries

def initial_cleaning(text):
	""" 
	Function to initial clean the bill text before infering spaces
	Params:
		text: a string of bill text
	"""
    # Remove all spaces and convert to lower case
	text = re.sub(r'\s+', "", text.lower())
    # Find the section headers and flag them with the phrase "sectionheaderflag" for future splitting
	header_expressions = [r'hb\d+', r'\\[a-z]+\b', r'\\\d+\b', r'hb\d+', r'sb\d+', r'hf\d+', r'sf\d+', r'\d+']
	for exp in header_expressions:
		text = re.sub(exp, "sectionheaderflag", text)
    # Remove additional punctuation
	final_text = re.sub(r'[^\w\s]', "", text)
	return final_text

def infer_spaces(s, worcost, maxword):
    """Uses dynamic programming to infer the location of spaces in a string without spaces
    Source code: https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words
    """
    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
	# Prepare string (lower and remove all spaces)
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)
    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)
    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k
    return " ".join(reversed(out))

def text_shortener(bill_text):
	"""
	Function to shorten bills so that they only begin on a phrase that marks the start of the bill text 
	(e.g. 'be enacted by...'); other uneccesary phrases will be removed too; section headers will be 
	replaced with numbers to be split on during document splitting
	Params:
		bill_text: a string of bill text
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
    # Common phrase among bill to remove
	s = re.sub(r'new text underlined deleted text bracketed', ' ', shortened_str, flags = re.IGNORECASE)
	# Remove any patterns of multiple letters separated by spaces: "a a a" or "aa"
	s = re.sub(r'\b(\w)\s?\1\s?\1\b', ' ', s)
	# Remove all single letter characters remaining except for "a" and "i" because those are actual full words
	s = re.sub(r'(?<!\b[a])\b\w\b(?!([a]\b|\w))', '', s)
	# Replace section headers with a period for splitting
	s = s.replace("section header flag", ".")
	# Returned shortened string
	return s.strip()

def splitter(text):
    """ 
    Function to split the clean bills into their section chunks
    Params:
        text: a string of text of a bill
    """
    split_text = text.split(".")
    split_text_stripped = [phrase.strip()for phrase in split_text]
    final_text_list = list(filter(lambda x: x != '', split_text_stripped))
    return final_text_list

def merge_data(indir):
	"""
	Function to merge the aclu, summary, and bill data into one data frame
	"""
	# Get the bill text
	bill_text_data = import_bill_texts(indir)
    # Get the ACLU table
	aclu_table = import_aclu(indir)
    # Get our bill summaries
	summary_data = import_summaries(indir)
    # Merge data frames
	merge1 = aclu_table.merge(bill_text_data, on = ["state", "bill_name"])
	merge_all = merge1.merge(summary_data, on = ["state", "bill_name"])
	# Clean up data frame
	merge_all = merge_all.drop("full_state_y", axis = 1)
	merge_all = merge_all.rename(columns = {"full_state_x": "state_name", "text": "original_text", "source": "summary_source"})
	return merge_all

def doc_splitting(l, max_token_len = 512):
	'''Function to split the documents dynamically to abide by token limit''' 
	# Initialize sum and list
	total_sum = 0
	idx_list = []
	# Iterate over each item in list
	for i,l in enumerate(l):
	  # Check if adding element to sum causes sum to be over limit
		if total_sum + l + 1 > max_token_len: # add 1 because the T-5 model only does an end token
			idx_list.append(i) # add split location to list of indices for splitting
			total_sum = 0 # reset to 0
		total_sum += l
	return idx_list

def text_split(l, idx):
  '''Function to split a list of text using a list of indices'''
  return [list(i) for i in np.split(np.array(l), idx)]

if __name__ == "__main__":

	startTime = time.time()
	timeTag = time.strftime('%Y%m%d_%H_%M_%S')

	# Read arguments
	parser = argparse.ArgumentParser(description="Code to evaluate fuzzy matching")
	parser.add_argument("-i", "--indir", required=True, help="Path to input files (ACLU text, bill text, etc.)")
	parser.add_argument("-s", "--split", help="Path to machine summaries data", action='store_false') # default is run non-doc split
	parser.add_argument("-o", "--outdir", required=True, help="Path to output and logging")
	args = parser.parse_args()	

	# Begin logger
	logger = setup_logger(f'log_{timeTag}.log', args.outdir)
	logger.info(f'Running Data Processing script. Start time {timeTag}')
	logger.info(f'Input file: {args.indir}')
	logger.info(f'Output directory: {args.outdir}')
	logger.info(f'Document Splitting Functionality: {args.split}')

	logger.info('Reading in datasets from the directory')
	data = merge_data(args.indir)
	# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability)
	words = open(os.path.join(args.indir, "our_words.txt")).read().split() #words = open("../../modified_data/our_words.txt").read().split()
	wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
	maxword = max(len(x) for x in words)

	logger.info('Beginning text cleaning on combined data')
	# Clean the text
	# Inital clean -> infer the spaces -> shorten the text -> split it
	data["cleaned_text"] = data["original_text"].apply(lambda x: text_shortener(infer_spaces(initial_cleaning(x), wordcost, maxword)))
	data["split_cleaned_text"] = data["cleaned_text"].apply(lambda x: splitter(x))
	# Combine state and bill name columns into id column
	data["bill_id"] = data["state"].astype(str) + " " + data["bill_name"].astype(str)
	
	logger.info('Filter to only keep bills with reference summaries')
	# Remove columns without text or summary
	filtered_data = data[data["keep"] == 1]

	if args.split:
		logger.info('Beginning document splitting')

		checkpoint = "t5-small"
		tokenizer = AutoTokenizer.from_pretrained(checkpoint)

		logger.info('Creating token list lengths')
		filtered_data['token_list'] = filtered_data['split_cleaned_text'].apply(lambda x: [tokenizer(i)["input_ids"] for i in x])
		# Calculate the length of the token list & split
		filtered_data['token_list_lens'] = filtered_data['token_list'].apply(lambda x: [len(i)-1 for i in x])
		filtered_data['split_idx_list'] = filtered_data['token_list_lens'].apply(lambda x: doc_splitting(x))
		# Split text using function
		filtered_data['split_text_512'] = filtered_data.apply(lambda x: text_split(x['split_cleaned_text'], x['split_idx_list']), axis=1)
		
		logger.info('Creating individual chunk rows')
		# Explode the split text 512 column so each row is one chunk
		filtered_data = filtered_data.explode('split_text_512', ignore_index=True)

		logger.info('Adding document number for each chunk and concatenating strings together')
		# Create a group by index number to keep track of chunks
		filtered_data['doc_number'] = filtered_data.groupby('bill_id')['split_text_512'].cumcount().add(1)
		# Concatenate string list items into single string
		filtered_data['split_text'] = filtered_data['split_text_512'].apply(lambda x: ' '.join(x))

		logger.info('Prepping for saving output')
		# Save output
		outputFile = os.path.join(args.outdir, f"text_and_summaries_filtered_split_{timeTag}.csv")
		# Reorder columns, include new split column and doc num col
		filtered_data = filtered_data[["state_name", "state", "bill_id", "bill_name", "doc_number", "split_text", "summary", "summary_source", "category", "status", "link"]]
	else:
		logger.info('Prepping for saving output')
		# Reorder columns
		filtered_data = filtered_data[["state_name", "state", "bill_id", "bill_name", "original_text", "cleaned_text", "split_cleaned_text", "summary", "summary_source", "category", "status", "link"]]
		# Save output file
		outputFile = os.path.join(args.outdir, f"text_and_summaries_filtered_{timeTag}.csv")
	# Make a csv of the filtered data
	filtered_data.to_csv(outputFile, index = False) #"../../modified_data/text_and_summaries_filtered.csv"
	endTime = time.time()
	endTag = time.strftime('%Y%m%d_%H_%M_%S')
	logger.info(f'Saved file to {outputFile}. Finished running at time {endTag}.')