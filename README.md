# BASL - Bill Abstractive Summarizer for LGBTQ+ Related Legislation


### Project Description

Our python package, named BASL, attempts to summarize legal text specifically relating to anti-LGBTQ+ legislation. One model was employed with dynamic text splitting; whereas, one model was employed without dynamic text splitting. The models are trained using Google's T5 Test-to-Text Transfor Transformer with a HuggingFace summarization pipeline. T5 is similar to BERT (Bidirectional Encoder Representations from Transformers ) in that it was trained using MLM (masked language modelling). The main difference is that T5 masked multiple consecutive words instead of just one, which makes it a better suited model for text-to-text problems. For evaluation, we used the ROUGE scoring metric. ROUGE evaluation may not be the best fit for abstractive summarization since it is rigid and does not capture semantic meaning. For our final product, we employed a Flask application with our summarizer models. 

An important takeaway is that LM token limitations can be mitigated by splitting text or by employing more sophisticated methods, such as embeddings. From this project, we learned that abstractive summarization has tremendous potential when dealing with long, domain-specific text in the legislative sphere. In terms of next steps, if we would continue this project, we would like to spend more time cleaning and preprocessing the text in this legal context to mitigate errors introduced when reading in the bill PDFs. We would also like to improve our reference summaries by bringing in experts i.e., lawyers. We would also investigate ways to improve summarization by finding other models or pre-training on text geared toward anti-LGBTQ+ detection. 

### How to Install and Run the Project

### Package Structure

```.
├── README.md
├── bin/
├── data_preprocessing/
├── eval/
├── models/
├── tests/
└── utils/
```

* How to run tests:
Navigate to the `/tests` directory, and run the command `python -m pytest tests/`

### How to Use the Project

### References
