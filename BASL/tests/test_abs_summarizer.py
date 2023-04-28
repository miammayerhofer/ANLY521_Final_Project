from pathlib import Path
from utils.bill_text_scraper import *
from utils.bill_text_cleaner_splitter import *
from utils.aclu_table_scraper import *
from abs_summarizer.abstractive_bill_summarizer import AbstractiveBillSummarizer
import numpy as np
import unittest
import pytest
import pandas as pd
import datasets

# make sure the bill_text_scraper is in the right format and reads in data
# PASSED
def test_bill_text_scraper():
    bills_df = read_files()
    assert ((list(bills_df.columns) == ['state', 'bill_name', 'text']) and (len(bills_df) > 0))

# make sure the bill_text_cleaner_splitter breaks up the text into chunks
# PASSED
def test_bill_text_cleaner_splitter():
    f = open(Path().absolute()/Path('tests')/Path('data')/Path('long_text.txt'), "r")
    long_text = f.read()
    my_splitter = BillTextSplitter(long_text)
    assert (len(my_splitter.split_text) > 0)


# make sure the aclu_table_scraper is in the right format and reads in the data
# PASSED
def test_aclu_table_scraper():
    aclu_url = "https://www.aclu.org/legislative-attacks-on-lgbtq-rights?impact=&state="
    # Run web driver
    aclu_table_html = scrape_table(aclu_url)
    # Make a data frame from the information
    df = get_table_info(aclu_table_html)
    # Convert to csv file
    df.to_csv("../modified_data/aclu_table_data.csv", index = False)
    assert ((list(df.columns) == ['state', 'link', 'bill_name', 'category', 'status']) and (len(df) > 0))


# make sure the summarizer outputs a string thats shorter than the actual text
# PASSED
def test_summarizer():
    model_output_path = Path().absolute()/'models'/'summarizer_model'
    df = pd.read_csv(Path().absolute()/Path('tests')/Path('data')/Path('test_bill_sum.csv'))
    train_df = df[df.dataset_type == 'train']
    test_df = df[df.dataset_type == 'test']
    train_dataset = datasets.Dataset.from_dict(train_df)
    test_dataset = datasets.Dataset.from_dict(test_df)
    billsum = datasets.DatasetDict({"train": train_dataset, "test": test_dataset})

    my_summarizer = AbstractiveBillSummarizer(output_directory_path = model_output_path,
        checkpoint = 't5-small',
        billsum_dataset = billsum
        )
    my_summarizer.model_directory = model_output_path
    test_summary = my_summarizer.test(test_df)
    assert ((type(test_summary) == list) and (len(' '.join(test_summary)) < len(' '.join(test_df.text))))