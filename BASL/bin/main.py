import argparse
from pathlib import Path
# from BASL.abs_summarizer import abs_summarizer
import pandas as pd
import datasets

# run script with `python main.py -nosplit file_name.csv`
if __name__ == "__main__":
    # the script requires a CSV file containing the bill texts 
    parser = argparse.ArgumentParser(
        description="Whether to use summarizer that splits documents or not")
    parser.add_argument("filename", help="File name with bill texts")
    parser.add_argument("-nosplit", '--nosplit_flag', help="Model type", action = 'store_true')
    args = parser.parse_args()

    # establish data directory and read in data
    data_dir = Path().absolute().parents[1]/Path("modified_data")
    input_file = Path(args.filename)
    df = pd.read_csv(data_dir/args.filename)
    
    # if the nosplit flag was turned on then use the summarizer that doesn't implement document splitting
    if args.nosplit_flag:
        model_output_path = Path().absolute()/'models'/'summarizer_model_not-split'   
    else:
        model_output_path = Path().absolute()/'models'/'summarizer_model'

    # create the dataset to pass into the summarizer    
    train_df = df[df.dataset_type == 'train']
    test_df = df[df.dataset_type == 'test']
    train_dataset = datasets.Dataset.from_dict(train_df)
    test_dataset = datasets.Dataset.from_dict(test_df)
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
    # write the new file with a suffix indicating its the output of the model
    new_file_name = input_file.stem + '(model_output)' + input_file.suffix
    df.to_csv(data_dir/new_file_name)

