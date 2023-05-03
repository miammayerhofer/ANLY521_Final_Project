import argparse
from pathlib import Path
# from BASL.abs_summarizer import abs_summarizer
# from abs_summarizer.abstractive_bill_summarizer import AbstractiveBillSummarizer
# import abs_summarizer
from BASL.abstractive_bill_summarizer import AbstractiveBillSummarizer
import pandas as pd
import datasets
import os

os.environ['KMP_DUPLICATE_LIB_OK']='True'

# run script with `python main.py text_and_summaries_filtered_split.csv`
# OR: `python main.py -nosplit text_and_summaries_filtered.csv`
if __name__ == "__main__":
    # the script requires a CSV file containing the bill texts 
    parser = argparse.ArgumentParser(
        description="Whether to use summarizer that splits documents or not")
    parser.add_argument("filename", help="File name with bill texts")
    parser.add_argument("-nosplit", '--nosplit_flag', help="Model type", action = 'store_true')
    args = parser.parse_args()

    # establish data directory and read in data
    # depending where this script is used it will navigate to find the /raw_data folder differently
    path_parts = Path().absolute().parts
    if Path().absolute().name == 'BASL':
        path = Path().absolute()/"raw_data"
    elif path_parts[len(path_parts)-2] == 'BASL':
        path = Path().absolute().parents[0]/"raw_data"
    data_dir = Path().absolute()/Path("modified_data")
    input_file = Path(args.filename)
    df = pd.read_csv(data_dir/args.filename)
    
    # if the nosplit flag was turned on then use the summarizer that doesn't implement document splitting
    if args.nosplit_flag:
        model_output_path = Path().absolute()/'models'/'summarizer_model_not-split'   
        df = df.rename({'cleaned_text': 'text'}, axis='columns')
    else:
        model_output_path = Path().absolute()/'models'/'summarizer_model'
        df = df.rename({'split_text': 'text'}, axis='columns')
    # create the dataset to pass into the summarizer    
    # train df will be arbitrary since we're not training the model and test will be the entire dataset
    df = df[['state', 'text', 'summary', 'bill_id']]
    train_df = df.head().copy(deep=True)
    test_df = df.copy(deep=True)
    print(test_df.head())
    train_dataset = datasets.Dataset.from_dict(train_df)
    test_dataset = datasets.Dataset.from_dict(test_df.astype(str))
    billsum = datasets.DatasetDict({"train": train_dataset, "test": test_dataset})

    # create the summarizer object
    my_summarizer = AbstractiveBillSummarizer(output_directory_path = model_output_path,
        checkpoint = 't5-small',
        billsum_dataset = billsum
        )
    my_summarizer.model_directory = model_output_path
    # run the summaries
    summaries = my_summarizer.test(df)
    df['model_summary'] = summaries
    if not args.nosplit_flag:
        # create the joined bill text 
        df.sort_values(by=['state', 'bill_id', 'doc_number'],
                             ascending=True,
                             inplace=True
                             )
        joined_bill_text = df.groupby(['state', 'bill_id', 'reference_summary'])['text'].apply(lambda x: ' '.join(x)).reset_index()
        # create the joined model summaries
        joined_model_summaries = df.groupby(['state', 'bill_id'])['model_summary'].apply(lambda x: ' '.join(x)).reset_index()
        # add to the first dataframe
        joined_text_df = joined_bill_text.merge(joined_model_summaries,
                                                left_on = ['state', 'bill_id'],
                                                right_on = ['state', 'bill_id'],
                                                how='inner')
        # create dummy variable doc_id since thats what the rouge score script expects
        joined_text_df['doc_number'] = 1
        df = joined_bill_text.copy(deep=True)
    # write the new file with a suffix indicating its the output of the model
    new_file_name = input_file.stem + '(model_output)' + input_file.suffix
    df.to_csv(data_dir/new_file_name)

