import numpy as np
import pandas as pd
from pandas.errors import ParserError
import matplotlib.pyplot as plt
from src.utils import get_project_root
from src.features.preprocess import PreProcess #DEPENDENCY

from bertopic import BERTopic
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from bs4 import BeautifulSoup
import contractions

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re
import contractions
from pprint import pprint

import os

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')


class BertModels:
    """
    BERT topic modeling and sentiment analysis pipeline class

    TODO: save_model function

        DELETE:fill_na: performs on the column itself
    """

    def __init__(self, subreddit='Music', sort_type='hot'):
        """
        BertModels object constructor

        :param subreddit: name of subreddit that succeeds 'r/'
        :param sort_type: order of submission sorting: 'hot' or 'new' 
        """
        # for sentiment analysis
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        self.tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

        self.data = None
        self.subreddit = subreddit
        p = get_project_root().joinpath('data/raw')
        try:
            self.posts_df = pd.read_csv(get_project_root().joinpath('data/raw').joinpath(f'{subreddit}_{sort_type}_posts.csv'))
            self.comments_df = pd.read_csv(get_project_root().joinpath('data/raw').joinpath(f'{subreddit}_{sort_type}_comments.csv'))
        except ParserError:
            self.posts_df = pd.read_csv(get_project_root().joinpath('data/raw').joinpath(f'{subreddit}_{sort_type}_posts.csv'), lineterminator='\n')
            self.comments_df = pd.read_csv(get_project_root().joinpath('data/raw').joinpath(f'{subreddit}_{sort_type}_comments.csv'), lineterminator='\n')
        self.model = None
        self.topics = None
        self.docs = None
        self.topic_probs = None

    def eda(self, tdf, pre='body'):
        """
        Performs Exploratory Data Analysis (EDA) on Reddit Submissions DataFrame.
            Displays a set of visualizations that provide a snapshot of the data.
            Total number of words, size of vocabulary, max entry length, frequency distribution of words per entry.

        :param tdf: DataFrame for EDA
        :param pre: column name to apply EDA
        """

        df = tdf.copy()
        prep = PreProcess()

        ###
        print('Remove Escape Characters')
        prep.remove_escape_chars(df, pre)

        print('Clean Special Characters')
        prep.clean_special_characters(df, pre)
        ###

        print("Number of Entries: ",df.shape[0])
        print("Columns: ",df.columns)

        all_words = [word for tokens in df[pre + '_word_token'] for word in tokens]
        post_lengths = [len(tokens) for tokens in df[pre + '_word_token']]
        vocab = sorted(list(set(all_words)))

        print('{} words total (after preprocessing), with a vocabulary size of {}'.format(len(all_words), len(vocab)))
        print('Max entry length is {}'.format(max(post_lengths)))

        flat_words = [item for sublist in df[pre + '_word_token'] for item in sublist]
        word_freq = FreqDist(flat_words)
        fdf = pd.DataFrame(word_freq.most_common(20), columns=['word', 'frequency'])
        fdf.plot(kind='bar', x='word', rot=70)
        plt.show()

        df[pre + '_length'] = df[pre].apply(lambda x: len(x.split()))
        print('Frequency Distribution of words per entry:')
        df[pre + '_length'].hist()
        plt.xlabel("Number of Words")
        plt.ylabel("Count of Entries")
        plt.show()

    def topic_preprocess(self, df, col):
        """
        Preprocess DataFrame and make ready for BERTopic modeling. 

        :param df: DataFrame with subreddit data to be processed
        :param col: column name to be processed
        """
        prep = PreProcess()

        print('Num rows: ', df.shape)
        temp = df.shape[0]
        df[col] = df[col].astype(str)
        df = df[df[col] != 'nan']
        df = df.reset_index()
        print('Num rows removed: ', temp - df.shape[0])

        print('Fill NaNs')
        prep.fill_na(df, col)

        print('Remove URLs')
        prep.remove_urls(df, col)

        print('Expand Contractions')
        prep.expand_contractions(df, col)

#         print('Remove Escape Characters')
#         prep.remove_escape_chars(df, col)

        print('Make Lowercase')
        prep.to_lower(df, col)

        print('Tokenize')
        prep.tokenize(df, col)

#         print('Clean Special Characters')
#         prep.clean_special_characters(df, col)

        print('Filter Stopwords')
        prep.filter_stopwords(df, col)

        print('Lemmatization')
        prep.lemm(df, col)
        
        return df

    def topic_modeling(self, df, col='body_word_token', calculate_probabilities=True, verbose=True, visualize=True):
        """
        Topic Modeling performed using BERTopic.

        :param df: Processed DataFrame ready for topic modeling
        :param col: Column to be processed
        :param calculate_probabilities:  
        """

        try:
            df['body_string'] = df[col].apply(lambda x: ' '.join(map(str, x)))
            body_df = df.reset_index()
        except:
            raise Exception('Need to preprocess')

        docs = list(body_df.body_string)
        self.docs = docs
        print('Number of entries being modeled:', len(docs))

        print('Intiailizing model and training')
        self.model = BERTopic(language="english", calculate_probabilities=calculate_probabilities, verbose=verbose)
        topics, probs = self.model.fit_transform(docs)
        self.topics = topics
        self.topic_probs = probs

        if visualize:
            if self.model==None:
                raise Exception('No model')

            self.topic_viz()

    def topic_viz(self):

        if self.model==None:
            raise Exception('No model')

        print('Top 5 Topics Frequency:')
        freq = self.model.get_topic_info()
        freq.plot(kind='bar', x='Name', y='Count', rot=70)
        plt.show()

        try:
            print('Intertopic Distance Map:')
            fig1 = self.model.visualize_topics()
            fig1.show()

            print('Topic Probability Distribution')
            fig2 = self.model.visualize_distribution(self.topic_probs[200], min_probability=0.015)
            fig2.show()

            print('Topic Word Scores')
            fig3 = self.model.visualize_barchart(top_n_topics=10)
            fig3.show()

        except:
            raise Exception('Not enough topics')

    def get_topics(self):

        if self.model==None:
            raise Exception('No model')

        print("Topics are:")
        print(self.model.get_topic_info())

        #NOTE: can also implement find topics

    def reduce_topics(self, nr_topics=10):

        if self.model==None:
            raise Exception('No model')

        new_topics, new_probs = self.model.reduce_topics(self.docs, self.topics, self.topic_probs, nr_topics=nr_topics)
        self.topics = new_topics
        self.probs = new_probs

        print("Updating topic model with reduced topics set.")
        self.model.update_topics(self.docs, self.topics, n_gram_range=(1, 3))

        # print('Reduced topic distributions:')
        # fig = self.model.visualize_barchart(top_n_topics=10)
        # fig.show()

    def save_topic_model(self, post=True):
        p = get_project_root().joinpath('models')
        p.mkdir(parents=True, exist_ok=True)
        if post:
            self.model.save(p.joinpath(f'bertopic-model-posts-{self.subreddit}'))
        else:
            self.model.save(p.joinpath(f'bertopic-model-comments-{self.subreddit}'))

    @staticmethod
    def load_topic_model(subreddit, post=True):
        try:
            if post:
                p = get_project_root().joinpath('models').joinpath(f'bertopic-model-posts-{subreddit}')
            else:
                p = get_project_root().joinpath('models').joinpath(f'bertopic-model-comments-{subreddit}')
            return BERTopic.load(p)
        except Exception:
            print("Model was not found!")

    def sentiment_preprocess(self, df, col):

        df[col] = df[col].astype(str)
        df = df[df[col] != 'nan']
        df = df.reset_index()

        prep = PreProcess()

        print('Fill NaNs')
        prep.fill_na(df, col)

        print('Remove URLs')
        prep.remove_urls(df, col)

        print('Expand Contractions')
        prep.expand_contractions(df, col)

        print('Remove escape characters.')
        prep.remove_escape_chars(df, col)

        return df

    def sentiment_analysis(self, df, col):

        def sentiment_score(post):
            '''
            For sentiment scoring of posts.
            '''
            tokens = self.tokenizer.encode(post, return_tensors='pt')
            result = self.sentiment_model(tokens)
            return int(torch.argmax(result.logits))+1

        df['sentiment'] = df[col].apply(lambda x: sentiment_score(x[:512]))
        return df

    def sentiment_viz(self, df):
        if 'sentiment' not in df.columns:
            raise Exception('No sentiments available')

        df.sentiment.value_counts().loc[[1, 2, 3, 4, 5]].plot(kind='bar', xlabel='sentiment', ylabel='frequency')
        pprint(df.sentiment.value_counts().loc[[1, 2, 3, 4, 5]])
        plt.show()
