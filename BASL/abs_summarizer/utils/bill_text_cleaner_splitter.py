import re
from math import log


class BillTextCleaner:
    def __init__(self, text, wordcost, maxword):
        """
        Initialize the BillTextCleaner class with an input text and parameters required for infering spaces
        """
        self.initial_text = text
        self.wordcost = wordcost
        self.maxword = maxword
        self.initial_clean()
        self.infer_spaces()
        self.text_shortener()

    def get_clean_text(self):
        return self.clean_text

    def initial_clean(self):
        """ 
	    Function to initial clean the bill text before infering spaces
        """
        # Remove all spaces and convert to lower case
        self.clean_text = re.sub(r'\s+', "", self.initial_text.lower())
        # Find the section headers and flag them with the phrase "sectionheaderflag" for future splitting
        header_expressions = [r'hb\d+', r'\\[a-z]+\b', r'\\\d+\b', r'hb\d+', r'sb\d+', r'hf\d+', r'sf\d+', r'\d+']
        for exp in header_expressions:
            self.clean_text = re.sub(exp, "sectionheaderflag", self.clean_text)
        # Remove additional punctuation
        self.clean_text = re.sub(r'[^\w\s]', "", self.clean_text)

    def infer_spaces(self):
        """
        Uses dynamic programming to infer the location of spaces in a string without spaces
        Source code: https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words
        """
        # Find the best match for the i first characters, assuming cost has been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length)
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i - self.maxword):i]))
            return min((c + self.wordcost.get(self.clean_text[i-k-1:i], 9e999), k+1) for k,c in candidates)
        # Build the cost array.
        cost = [0]
        for i in range(1,len(self.clean_text)+1):
            c, k = best_match(i)
            cost.append(c)
        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(self.clean_text)
        while i > 0:
            c, k = best_match(i)
            assert c == cost[i]
            out.append(self.clean_text[i-k:i])
            i -= k
        self.clean_text = " ".join(reversed(out))

    def text_shortener(self):
        """
        Function to shorten bills so that they only begin on a phrase that marks the start of the bill text 
        (e.g. 'be enacted by...'); other uneccesary phrases will be removed too; section headers will be 
        replaced with numbers to be split on during document splitting
        """
        enact_str = r"be it enacted by|enact as follows|state of [a-z]+ enact|assembly of [a-z ]+ enact"
        # Find where the bill is enacted
        if re.search(enact_str, self.clean_text.lower()):
            enacted_by_index = re.search(enact_str, self.clean_text.lower()).start() 
        else:
            enacted_by_index = 0
        self.clean_text = self.clean_text[enacted_by_index:]
        # Start at the section
        if "section" in self.clean_text.lower():
            first_section_index = re.search("section", self.clean_text.lower()).start()
        else:
            first_section_index = 0
        self.clean_text = self.clean_text[first_section_index:]
        # Common phrase among bill to remove
        self.clean_text = re.sub(r'new text underlined deleted text bracketed', ' ', self.clean_text, flags = re.IGNORECASE)
        # Remove any patterns of multiple letters separated by spaces: "a a a" or "aa"
        self.clean_text = re.sub(r'\b(\w)\s?\1\s?\1\b', ' ', self.clean_text)
        # Remove all single letter characters remaining except for "a" and "i" because those are actual full words
        self.clean_text = re.sub(r'(?<!\b[a])\b\w\b(?!([a]\b|\w))', '', self.clean_text)
        # Replace section headers with a period for splitting
        self.clean_text = self.clean_text.replace("section header flag", ".")
        self.clean_text.strip()

class BillTextSplitter:
    def __init__(self, text):
        """
        Initialize the BillTextSplitter class with an input text
        """
        self.text = text
        self.splitter()
    
    def get_split_text(self):
        return self.split_text

    def splitter(self):
        """ 
        Function to split the clean bills into their section chunks
        """
        # Split on periods set while cleaning the data
        self.split_text = self.text.split(".")
        self.split_text = [phrase.strip()for phrase in self.split_text]
        self.split_text =  list(filter(lambda x: x != '', self.split_text))