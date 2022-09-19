# Topic-Sentiment Analysis and Relevance System (TSAR) - BEReddiT
![Heroku](https://heroku-status-badges.herokuapp.com/bereddit-dash)
![Python](https://img.shields.io/badge/python-v3.7.12-blue)
[![MIT License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/reddit-conflicting-viewpoints/Reddit/blob/main/LICENSE)

<p align="center">
  <img src="https://github.com/reddit-conflicting-viewpoints/Reddit/blob/main/assets/bereddit-logo.png" />
</p>

**By: Andrew Zhou, Sai Muktevi, Preston Stringham, Hasnah Said**

Web Visualization Dashboard is deployed on [appspot](https://bereddit-tsar.wl.r.appspot.com/) and [heroku](http://bereddit-dash.herokuapp.com/).

**Project Poster and Flyer**  
Project Poster can be found [here](https://github.com/reddit-conflicting-viewpoints/Reddit/blob/main/reports/TSAR_POSTER.pdf).  
Project Flyer can be found [here](https://github.com/reddit-conflicting-viewpoints/Reddit/blob/main/reports/Flyer.pdf).  

## Introduction

With the advent of popular social media or forums and their power in swaying decision-making due to sensationalization of various topics of discussion, it seems to be reasonable to look for polarizing discussion on such platforms. Reddit.com is one of the most popular websites used to discuss and share ideas with like-minded users due to its well-organized structure. Reddit consists of a database of forums referred to as “subreddits” which contain posts about specific topics. Each subreddit has at least one “moderator” who is in charge of the content that is posted on their subreddit. With over 430 million monthly active users and >100,000 active subreddits, Reddit has provided people with a platform to express (potentially radical) ideas and debate on various levels from mundane to extreme topics of discussion.  

Bias in opinion is the driving force behind extreme opposition from different sides in a polarizing discussion. This "extremism" can lead to conflict with no side leaning into a compromising state of resolution. Oftentimes when a debate reaches a level of acute polarization, bias sways different people to incline to different perspectives without giving much thought to the holistic viewpoint. This encouraged us to pursue the idea of understanding, observing and finding ways to uncover these conflicting viewpoints to obtain balanced information from a discussion at hand.  

We aim to understand how we can use current approaches to natural language processing to understand the semantics of debate and biased discussion by uncovering conflicting viewpoints. On a social level, we aim to create an impact in such forums to enable balanced debates on varying perspectives to show respect to all views with reasonable arguments.
 
**What is the TSAR System?**
 
The TSAR System is a complex data engineering pipeline that utilizes Natural Language Processing to analyze internet forum discussions using dedicated APIs depending on the source of data.
Here we use Reddit APIs to access data from various subreddits.
The TSAR system is powered by BERT word embeddings and the system consists of multiple components that you will see in the various pages of this application, which are as follows:
* Topic Modeling - To find topics in Posts and Comments
* Sentiment Analysis - To find sentiments of Posts and Comments.
* Relevance Score - To observe the relevance of Comments with respect to their Posts.
* Conflicting Viewpoints - To observe the results of TSAR on the selected subreddit.

## Installation and Setup
This tutorial will allow you to run the code locally on your own machine!  
*It is recommended that you create a new conda environment (if you have conda) or a new virtual environment before installation.*

1) Clone the git repository to your local machine and change directory to recipeat
```
git clone https://github.com/reddit-conflicting-viewpoints/Reddit.git
cd Reddit
```
2) Install required packages and dependecies. This installs from our `setup.py` file.
```
pip install -r requirements.txt
```
3) You're ready to start running our app locally!  

* Run dash application
```
python app.py
```
* Run the scraper
```
python src/data/scraper.py
```
Note: scraper.py has the following arguments:  
1) Subreddit: '-s' or '--subreddit'. The subreddit to scrape from. Will scrape 'computerscience' by default.

2) Order: '-o' or '--order'. The order the scraper will scrape from. Will scrape 'hot' by default.

3) Maximum Post: '-mp' or '--maxpost'. The maximum number of posts the scraper can scrape. 1000 by default 

4) Maximum Comment Post: '-mcp' or '--maxcommentpost'. The maximum number of comments that can be scraped per post. 100 by default

5) Maximum Comment: '-mc' or '--maxcomment'. The maximum number of comments the scraper can scrape. 10000 by default. Note: The scraper may go over 10000 by a little bit

* Run BERT for topic modeling, sentiment analysis, and relevance analysis
```
python src/models/subreddit_analysis.py
```
Note: This module has to be run after scraper.py. subreddit_analysis.py has the following arguments:  
1) Subreddit: '-s' or '--subreddit'. The subreddit to analyze from. Will analyze 'computerscience' by default.

2) Order: '-o' or '--order'. The order the scraper had scraped from. 'hot' by default.

3) Maximum Post: '-mp' or '--maxpost'. The maximum number of posts to analyze. 2000 by default 

4) Maximum Comment: '-mc' or '--maxcomment'. The maximum number of comments to analyze. 20000 by default.

## Data Handling

### Downloading data
```
make data
```

```
python src/data/scraper.py
```
Recommended running `python src/data/scraper.py` as this allows argument parsing.  

Files will be downloaded to data/raw/.

### Syncing your data to azure blob
```
make sync_data_to_blob
```
Files in data/ will be synced to azure blob.

### Syncing your data from azure blob
```
make sync_data_from_blob
```
Fetch files in azure blob to your local machine. Note: If you have a file with the same name on azure blob, those files will not sync.  
Example: computerscience_comments.csv is on your local machine, and a new version of computerscience_comments.csv is on azure blob. The new version of computerscience_comments.csv on azure blob will not replace the local copy. 
