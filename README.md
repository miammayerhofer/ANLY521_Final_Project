# BASL - Bill Abstractive Summarizer for LGBTQ+ Related Legislation


### Project Description

BASL is a Python package that summarizes legal text related to anti-LGBTQ+ legislation. 

_Models_

The package contains two summarization models. One model is employed with dynamic text splitting and one without. BASL's models are trained using Google's T5 Test-to-Text Transfer Transformer with a HuggingFace summarization pipeline. T5 is similar to BERT (Bidirectional Encoder Representations from Transformers ) in that it is trained using MLM (masked language modeling). The main difference is that T5 masks multiple consecutive words instead of just one, which makes it better suited for text-to-text problems. 

_Evaluation_ 

We have evaluated the models using the ROUGE scoring metric, although we acknowledge that ROUGE evaluation may not be the best fit for abstractive summarization because it is rigid and does not capture semantic meaning. 

_Application_

For our final product, we have employed a Flask application with our BASL summarizer models. 

### BASL Package Structure

```.
├── BASL/
│   ├── README.md
│   ├── bin/
│   ├── data_preprocessing/
│   ├── environment.yml
│   ├── eval/
│   ├── models/
│   ├── modified_data/
│   ├── pytest.ini
│   ├── raw_data/
│   ├── setup.py
│   ├── tests/
│   └── utils/
├── flask_app/
│   ├── static/
│   ├── templates/
│   ├── app.py
│   ├── bill_text_cleaner_splitter.py
│   └── our_words.py
└── README.md

```

### How to Install and Run BASL

To install this package, clone this directory into your machine and run the following command:

```
pip install -e .
```

### How to Use BASL

**Important:** Download the following folders locally and place them in `BASL/models/` to run the package.

* summarizer_model_not-split/ https://drive.google.com/drive/folders/1--elIUBVds11Rz72prPNaNp9WDR-DKJ3
* summarizer_model/ https://drive.google.com/drive/folders/1bXGRq1weuXmzy7W_yLtjSzLkD4ndjE9y

To run the model (after download) create summaries *without* splitting, navigate to the `/bin` directory and run the command `python main.py text_and_summaries_filtered.csv -nosplit`

To run the model (after download) create summaries *with* splitting, navigate to the `/bin` directory and run the command `python main.py text_and_summaries_filtered_split.csv`

To run tests, navigate to the `/tests` directory, and run the command `python -m pytest tests/`

To run Rouge evaluation on completed model summaries from the `/eval` directory, run the command `python eval_rouge.py -f ../modified_data/model_and_reference_summaries_split.csv -o ../modified_data`

### Future Steps 

An important takeaway from this project is that LM token limitations can be mitigated by splitting text or by employing more sophisticated methods, such as embeddings. From this project, we have learned that abstractive summarization has tremendous potential when dealing with long, domain-specific text in the legislative sphere. 

In terms of next steps, if we were to continue this project, we would like to spend more time cleaning and preprocessing the text in this legal context to mitigate errors introduced when reading in bill PDFs. We would also like to improve our reference summaries by bringing in experts such as lawyers. Additionally We would investigate ways to improve summarization by finding other models or pre-training on text geared toward anti-LGBTQ+ detection. 

### References

* HF Tutorial w/ Bill Summarization: https://huggingface.co/docs/transformers/main/tasks/summarization
* Inferring Spacing Code: https://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words
* PDF Reading Code: https://gist.github.com/averagesecurityguy/ba8d9ed3c59c1deffbd1390dafa5a3c2
* Summary Sources: 
  * LegiScan https://legiscan.com/
  * FastDemocracy https://fastdemocracy.com/
  * LexisNexis https://www.lexisnexis.com/
  * State legislature sites
  * Bill Texts: State Legislature Sites
* ROUGE Scoring: https://aclanthology.org/W04-1013.pdf
* Flask Template: https://alaminmusamagaga.medium.com/text-summarization-app-with-flask-and-sumy-92212bd05705
* T-5 Information: https://turbolab.in/abstractive-summarization-using-googles-t5/
* Chat GPT for coding and debugging questions

### Contact

BASL GitHub @miammayerhofer, @corrinac, @mventura4, @jojomazel

Project link: https://github.com/miammayerhofer/ANLY521_Final_Project/
