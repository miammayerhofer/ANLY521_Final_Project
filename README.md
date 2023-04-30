# BASL - Bill Abstractive Summarizer for LGBTQ+ Related Legislation


### Project Description

BASL is a Python package that summarizes legal text related to anti-LGBTQ+ legislation. The package contains two summarization models. One model is employed with dynamic text splitting and one without. 

BASL's models are trained using Google's T5 Test-to-Text Transfer Transformer with a HuggingFace summarization pipeline. T5 is similar to BERT (Bidirectional Encoder Representations from Transformers ) in that it is trained using MLM (masked language modeling). The main difference is that T5 masks multiple consecutive words instead of just one, which makes it better suited for text-to-text problems. 

We have evaluated the models using the ROUGE scoring metric, although we acknowledge that ROUGE evaluation may not be the best fit for abstractive summarization because it is rigid and does not capture semantic meaning. 

For our final product, we have employed a Flask application with our BASL summarizer models. 

### How to Install and Run BASL

### BASL Package Structure

```.
├── BASL/
│   ├── README.md
│   ├── abs_summarizer/
│   ├── abs_summarizer.egg-info/
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
├── code/
├── flask_app/
├── modified_data/
├── raw_data/
├── README.md
└── rouge_results/

```

* How to run tests:
Navigate to the `/tests` directory, and run the command `python -m pytest tests/`

### How to Use BASL

### Future Steps 

An important takeaway from this project is that LM token limitations can be mitigated by splitting text or by employing more sophisticated methods, such as embeddings. From this project, we have learned that abstractive summarization has tremendous potential when dealing with long, domain-specific text in the legislative sphere. 

In terms of next steps, if we were to continue this project, we would like to spend more time cleaning and preprocessing the text in this legal context to mitigate errors introduced when reading in bill PDFs. We would also like to improve our reference summaries by bringing in experts such as lawyers. Additionally We would investigate ways to improve summarization by finding other models or pre-training on text geared toward anti-LGBTQ+ detection. 

### References

### Acknowledgements

BASL uses the following third-party libraries:

* NumPy
* Pandas
* T5 Transfer
* HuggingFace summarization pipeline
* ROUGE
* Flask


### Contact

BASL GitHub @miammayerhofer, @corrinac, @mventura4, @jojomazel

Project link: https://github.com/miammayerhofer/ANLY521_Final_Project/