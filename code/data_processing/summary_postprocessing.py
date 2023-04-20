import pandas as pd

def read_files():
    train_bills = pd.read_csv("../../modified_data/train_bills.csv").reset_index(drop = True).drop(["Unnamed: 0"], axis = 1)
    train_bills.columns = ["text", "reference_summary", "bill_id"]
    train_bills["dataset_type"] = "train"
    test_bills = pd.read_csv("../../modified_data/test_bills.csv").reset_index(drop = True).drop(["Unnamed: 0"], axis = 1)
    test_bills.columns = ["text", "reference_summary", "bill_id"]
    test_bills["dataset_type"] = "test"
    model_summaries = pd.read_csv("../../modified_data/model_summaries.csv")
    return train_bills, test_bills, model_summaries


if __name__ == "__main__":
    # Read in the model summaries and train and test info
    train_bills, test_bills, model_summaries = read_files()
    # Combine train and test
    merge_train_test_df = pd.concat([train_bills, test_bills], ignore_index = True)
    # Merge with model summaries
    merged_df = pd.merge(merge_train_test_df, model_summaries, on = "bill_id")
    merged_df.drop(["Unnamed: 0"], axis = 1, inplace = True)
    merged_df.to_csv("../../modified_data/model_and_reference_summaries.csv")

