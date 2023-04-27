import abs_summarizer.abstractive_bill_summarizer as abs
import pandas as pd
import datasets

from pathlib import Path
from sklearn.model_selection import train_test_split

if __name__ == "__main__":

    # Load data
    data = pd.read_csv(Path().absolute().parents[1]/Path("modified_data")/"text_and_summaries_filtered_split.csv")
    no_summary_filter = data.state == "IN" # subset to just one state for the test run
    all_text = data[no_summary_filter].copy(deep=True)
    cols_keep = ["state", "state_name", "bill_name", "summary", "doc_number", "split_text"]
    data = data[cols_keep]
    data.rename({"bill_name": "title", "split_text": "text",}, axis = "columns", inplace = True)

    # Split data
    train, test = train_test_split(data[["text", "summary"]], test_size = 0.2)
    train_dataset = datasets.Dataset.from_dict(train.astype(str))
    test_dataset = datasets.Dataset.from_dict(test.astype(str))
    billsum = datasets.DatasetDict({"train": train_dataset, "test": test_dataset})

    # Set inputs for model object
    output_directory_path = Path().absolute().parents[1]/Path("modified_data")
    model_directory_path =  Path().absolute()/Path("summarizer_model")
    checkpoint = "t5-small"

    # Define summarizer model
    model = abs.AbstractiveBillSummarizer(output_directory_path, checkpoint, billsum)
    model.train()
    model.save(model_directory_path)
    # Test on a bill
    test_bill = data[(data.state == "IN") & (data.title == "HB1118")]
    model.test(test_bill)

