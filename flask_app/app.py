# Template Source: https://alaminmusamagaga.medium.com/text-summarization-app-with-flask-and-sumy-92212bd05705

import time
import spacy
import numpy as np

from math import log
from flask import Flask,render_template,url_for,request
from transformers import AutoTokenizer, pipeline
from bill_text_cleaner_splitter import BillTextCleaner, BillTextSplitter

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

def summarizer(split_text, model_type):
   """Function to calculate the summary from the cleaned input text depending on the input model"""
   model_summary = ""
   if model_type == "t5-split":
      # Build the summarizer pipeline
      summarizer = pipeline("summarization", model = str("summarizer_model"))
      # Get the summary by section and append to overall summary
      for section in split_text:
         model_summary += summarizer(" ".join(section))[0]["summary_text"]
   elif model_type == "t5-no-split":
      # Build the summarizer pipeline
      summarizer = pipeline("summarization", model = str("summarizer_model_not-split"))
      # Summarizer on full text
      model_summary = summarizer(" ".join(split_text))[0]["summary_text"]
   return model_summary

def text_preprocessing(text):
   """Function to process the bill text"""
   words = open("our_words.txt").read().split()
   wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
   maxword = max(len(x) for x in words)
   clean_text = BillTextCleaner(text, wordcost, maxword).get_clean_text()
   split_clean_text = BillTextSplitter(clean_text).get_split_text()
   return split_clean_text

def doc_splitter(split_text):
   """Function to dynamically split the text to abide by the 512 token limit"""
   # Define tokenizer
   checkpoint = "t5-small"
   tokenizer = AutoTokenizer.from_pretrained(checkpoint)
   # Get list of tokens
   token_list = [tokenizer(i)["input_ids"] for i in split_text]
   # Get length of each chunk
   token_list_len = [len(i)-1 for i in token_list]
   total_sum = 0
   idx_list = []
   for i,l in enumerate(token_list_len):
      if total_sum + l + 1 > 512: 
         # Add split location to list of indices for splitting
         idx_list.append(i) 
         # Reset to 0
         total_sum = 0 
      total_sum += l
   # Split into chunks
   return [list(i) for i in np.split(np.array(split_text), idx_list)]

def readingTime(mytext):
   """Function to calculate the reading time of the bill text and summary"""
   total_words = len([ token.text for token in nlp(mytext)])
   estimatedTime = total_words/200.0
   return estimatedTime

@app.route('/')
def index():
   return render_template("index.html")
@app.route('/process',methods=['GET','POST'])
def process():
      start = time.time()
      if request.method == "POST":
         input_text = request.form["input_text"]
         model_choice = request.form["model_choice"]
         final_reading_time = readingTime(input_text)
         if model_choice == "t5-split":
            clean_split_text = doc_splitter(text_preprocessing(input_text))
            final_summary = summarizer(clean_split_text, "t5-split")
         elif model_choice == "t5-no-split":
            clean_text = text_preprocessing(input_text)
            final_summary = summarizer(clean_text, "t5-no-split")
      summary_reading_time = readingTime(final_summary)
      end = time.time()
      final_time = end-start
      return render_template("result.html", ctext = input_text,
                              final_reading_time = final_reading_time, 
                              final_time = round(final_time,2), 
                              summary_reading_time = summary_reading_time,
                              final_summary = final_summary,
                              model_selected = model_choice)

app.run(host = "0.0.0.0", port = 8000)