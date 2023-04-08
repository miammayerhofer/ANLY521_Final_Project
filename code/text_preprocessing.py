# IMPORT PACKAGES
from pathlib import Path
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import re
import wordninja
import ast


"""
Given a bill text, it finds the section of the PDF where the bill is enacted
and returns only the text after that
Enacting bill texts:
- be it enacted by
- enact as follows
- state of [state name] enact
- assembly of [state name] enact
"""
def text_shortener(bill_text):
	enact_str = r"be it enacted by|enact as follows|state of [a-z]+ enact|assembly of [a-z ]+ enact"
	# find where the bill is enacted
	if re.search(enact_str, bill_text.lower()):
		enacted_by_index = re.search(enact_str, bill_text.lower()).start() 
	else:
		enacted_by_index = 0
	shortened_str = bill_text[enacted_by_index:]
	# start at the section
	if "section" in shortened_str.lower():
		first_section_index = re.search("section", shortened_str.lower()).start()
	else:
		first_section_index = 0
	shortened_str = shortened_str[first_section_index:]
	# remove digits
	shortened_str = re.sub(r' [0-9]+ | [0-9]+[A-Z] ', ' ', shortened_str)
	# list of other strings to remove
	str_to_remove = ['NewTextUnderlinedDELETEDTEXTBRACKETED']
	shortened_str = re.sub('|'.join(str_to_remove), '', shortened_str)
	# remove section headers
	shortened_str = re.sub('section [0-9]+[a-z] ?', ' ', shortened_str, flags=re.IGNORECASE)
	return(shortened_str)

# Function to tokenize each line of a bill with word ninja
def word_ninja_tokenize(string):
	# remove spaces
	stripped = string.replace(' ', '')
	# use word ninja to infer words
	inferred_words = wordninja.split(string)
	# join words back together
	cleaned_text = ' '.join(inferred_words)
	return cleaned_text


if __name__ == "__main__":
	# read in file
	df = pd.read_csv(Path().absolute().parents[0]/Path("modified_data")/"bill_texts_full_text.csv")
	# use word ninja to clean words that might be separated
	df['cleaned_text'] = df['text'].apply(lambda x: word_ninja_tokenize(x))
	print("done inferring with ninja text")
	# shorten the text
	df['cleaned_text'] = df['cleaned_text'].apply(lambda x: text_shortener(x))
	df.to_csv(Path().absolute().parents[0]/Path("modified_data")/"bill_texts_full_text.csv", index=False)