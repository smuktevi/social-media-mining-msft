import pandas as pd
import numpy as np
from pandas.errors import ParserError

AZURE_URL = "https://redditconflict.blob.core.windows.net/redditconflict/results/"
SAS_KEY = "?sp=r&st=2022-03-06T23:29:32Z&se=2023-01-01T07:29:32Z&sv=2020-08-04&sr=c&sig=%2FGHaPmXaEBpc36JBlYfMJLPE8dYr5cFcAsbPpjV16NA%3D"

def get_csv_url(subreddit, sort_order='hot', results=True):
    local = "C:/Users/vmuktevi/Documents/Project/SocialMediaMining/Reddit/data/results/"
    if results:
        return local + subreddit + "_" + sort_order + "_results.csv"
    else:
        return local + subreddit + "_" + sort_order + "_subreddit.csv"
    # if results:  
    #     return AZURE_URL + subreddit + "_" + sort_order + "_results.csv" + SAS_KEY
    # else:
    #     return AZURE_URL + subreddit + "_" + sort_order + "_subreddit.csv" + SAS_KEY

def get_df(subreddit, sort_order='hot'):
    dtypess ={
        'post_index': int,
        'post_id': str,
        'post_title': str,
        'flair': str,
        'post_score': int,
        'post_upvote_ratio': np.float64,
        'subreddit': str,
        'post_url': str,
        'num_comments': int,
        'post_body': str,
        'post_created': int,
        'post_body_word_token': str,
        'post_body_tag': str,
        'post_body_string': str,
        'post_topics': str,
        'post_sentiment': int,
        'comment_index': pd.Int64Dtype(),
        'comment_id': str,
        'parent_id': str,
        'comment': str,
        'comment_score': pd.Int64Dtype(),
        'comment_controversiality': pd.Int64Dtype(),
        'comment_total_awards_received': pd.Int64Dtype(),
        'comment_is_locked': pd.BooleanDtype(),
        'comment_is_collapsed': pd.BooleanDtype(),
        'comment_is_submitter': pd.BooleanDtype(),
        'comment_created': pd.Int64Dtype(),
        'comment_word_token': str,
        'comment_tag': str,
        'comment_body_string': str,
        'comment_topics': str,
        'comment_sentiment': pd.Int64Dtype(),
        'comment_relevance': np.float64
    }
    try:
        df = pd.read_csv(get_csv_url(subreddit, sort_order))
        # df = pd.read_csv(get_csv_url(subreddit, sort_order), dtype=dtypess)
    except ParserError:
        df = pd.read_csv(get_csv_url(subreddit, sort_order), lineterminator='\n')
        # df = pd.read_csv(get_csv_url(subreddit, sort_order), lineterminator='\n', dtype=dtypess)
    return df

def get_df_description(subreddit, sort_order='hot'):
    try:
        df = pd.read_csv(get_csv_url(subreddit, sort_order, False))
    except ParserError:
        # print('ERROR: File Not Read')
        df = pd.read_csv(get_csv_url(subreddit, sort_order, False), lineterminator='\n')
    return df
