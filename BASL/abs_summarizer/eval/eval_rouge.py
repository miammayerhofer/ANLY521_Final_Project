import argparse
from rouge import Rouge
import pandas as pd
import ast
import logging
import time
import os

def setup_logger(log_file_name, log_dir_path):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_file_path = os.path.join(log_dir_path, log_file_name)
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

if __name__ == "__main__":

    startTime = time.time()
    timeTag = time.strftime('%Y%m%d_%H_%M_%S')

    # Read arguments
    parser = argparse.ArgumentParser(description="Code to evaluate fuzzy matching")
    parser.add_argument("-f", "--indir", required=True, help="Path to machine summaries data")
    parser.add_argument("-o", "--outdir", required=True, help="Path to logging")
    args = parser.parse_args()

    # Begin logger
    logger = setup_logger(f'log_{timeTag}.log', args.outdir)
    logger.info('Running Rouge evaluation script')

    logger.info(f'Input file: {args.indir}')
    logger.info(f'Output directory: {args.outdir}')

    # Read in summaries
    df = pd.read_csv(args.indir)

    logger.info('Read in data. Converting model summary into proper formatting')
    # Format the model summary column
    #df['model_summary'] = df['model_summary'].apply(lambda x: ast.literal_eval(x))
    #df['model_summary'] = df['model_summary'].apply(lambda x: ' '.join(x))

    # Initialize rouge
    rouge = Rouge()

    # Compute scores
    logger.info('Computing Rouge scores')
    try:
        df['scores'] = df.apply(lambda x: rouge.get_scores(x['model_summary'], x['reference_summary']), axis = 1)
    except:
        df['scores'] = df.apply(lambda x: rouge.get_scores(x['model_summary'], x['summary']), axis = 1)
    result = [pd.json_normalize(i) for i in df['scores']]
    result = pd.concat(result, ignore_index = True)

    # Add rouge score columns into dataframe
    df = pd.merge(df, result, left_index=True, right_index=True)

    results = df.groupby('dataset_type')[['rouge-1.r', 'rouge-1.p', 'rouge-1.f', 'rouge-2.r', 
                                'rouge-2.p', 'rouge-2.f', 'rouge-l.r', 'rouge-l.p', 'rouge-l.f']].mean().T
    logger.info('Breakdown of rouge scores by dataset type')
    logger.info(f'\n{results}')
    outputName = os.path.join(args.outdir, f'rouge_results_{timeTag}.csv')
    logger.info(f'Saving results: {outputName}')
    
    try:
        df[['text', 'reference_summary', 'bill_id', 'dataset_type', 'model_summary', 'rouge-1.r', 'rouge-1.p', 'rouge-1.f',
            'rouge-2.r', 'rouge-2.p', 'rouge-2.f', 'rouge-l.r', 'rouge-l.p','rouge-l.f']].to_csv(outputName, index = False)
    except:
        df[['text', 'summary', 'title', 'dataset_type', 'model_summary', 'rouge-1.r', 'rouge-1.p', 'rouge-1.f',
            'rouge-2.r', 'rouge-2.p', 'rouge-2.f', 'rouge-l.r', 'rouge-l.p','rouge-l.f']].to_csv(outputName, index = False)
    