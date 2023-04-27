import pandas as pd
import numpy as np
import datasets
import re
import time
import math
import evaluate
import torch

from transformers import pipeline
from pathlib import Path
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
from transformers import DataCollatorForSeq2Seq
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer


class AbstractiveBillSummarizer:
    """
    Perform abstractive summarization on an anti-LGBTQ+ bill 
    """
    def __init__(self, output_directory_path, checkpoint, billsum_dataset):
        """
        Define an AbstractiveBillSummarizer object
        Params:
            output_directory_path: path to the output of the model
            checkpoint: define a checkpoint for the tokenizer
            billsum_dataset: DatasetDict containing a train dataset and test dataset
        """
        self.output_directory = Path().absolute().parents[1]/Path(output_directory_path)
        self.checkpoint = checkpoint
        self.billsum = billsum_dataset
        # Define the tokenizer
        self.load_tokenizer()
        # Process and prepare the data
        self.prepare_data()
        # Define the initial model
        self.define_model()
        
    def load_tokenizer(self):
        """
        Method to load a tokenizer based on the input checkpoint
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint)
    
    def preprocess_function(self, examples):
        """
        Method that preprocesses the text by tokenizationa and truncation for the summarization
        Params:
            examples: a DataSetDict 
        """
        prefix = "summarize: "
        inputs = [prefix + doc for doc in examples["text"]]
        model_inputs = self.tokenizer(inputs, max_length = 1024, truncation = True)
        # Tokenizes and truncates
        labels = self.tokenizer(text_target = examples["summary"], max_length = 128, truncation = True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    def prepare_data(self):
        """
        Method that  tokenizes and processes the text data and defines a collator for the model
        """
        self.tokenized_billsum = self.billsum.map(self.preprocess_function, batched = True)
        self.data_collator = DataCollatorForSeq2Seq(tokenizer = self.tokenizer, model = self.checkpoint)

    def compute_metrics(self, eval_pred):
        """
        Methood that passes predictions and labels to compute the ROUGE metric - used for model training
        """
        rouge = evaluate.load("rouge")
        predictions, labels = eval_pred
        decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)
        result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
        prediction_lens = [np.count_nonzero(pred != self.tokenizer.pad_token_id) for pred in predictions]
        result["gen_len"] = np.mean(prediction_lens)
        return {k: round(v, 4) for k, v in result.items()}

    def define_model(self):
        """
        Method to define the model for training
        """
        model = AutoModelForSeq2SeqLM.from_pretrained(self.checkpoint)
        training_args = Seq2SeqTrainingArguments(
        #   output_dir = "/content/gdrive/My Drive/my_awesome_billsum_model",
            output_dir = self.output_directory,
            evaluation_strategy = "epoch",
            learning_rate = 2e-5,
            per_device_train_batch_size = 16,
            per_device_eval_batch_size = 16,
            weight_decay = 0.01,
            save_total_limit = 3,
            num_train_epochs = 4,
            predict_with_generate = True,
        #   fp16 = True,
            push_to_hub = False, # changed to false
        )

        self.trainer = Seq2SeqTrainer(
            model = model,
            args = training_args,
            train_dataset = self.tokenized_billsum["train"],
            eval_dataset = self.tokenized_billsum["test"],
            tokenizer = self.tokenizer,
            data_collator = self.data_collator,
            compute_metrics = self.compute_metrics,
        )

    def train(self):
        """
        Method to train the model 
        """
        start = time.time()
        self.trainer.train()
        end = time.time()
        print((end - start)/60)
    
    def save(self, model_directory):
        """
        Method to save the model
        Params:
            model_directory: an input directory to save the model to
        """
        self.model_directory = model_directory
        self.trainer.save_model(self.model_directory)

    def test(self, test_bill_text):
        """
        Method to test the model on a new input bill text
        Params:
            test_bill_text: input text for the model to summarize
        """
        summarizer = pipeline("summarization", model = str(self.model_directory))
        compiled_summary = []
        for each_bill_part in list(test_bill_text.text):
            model_summary = summarizer(each_bill_part)
            compiled_summary.append(model_summary[0]['summary_text'])

        print("Actual Summary:\n\t", test_bill_text.summary.unique())
        print("Model Summary:\n\t", ' '.join(compiled_summary))
        return compiled_summary

