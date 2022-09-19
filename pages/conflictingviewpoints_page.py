from dash import dcc, html, Input, Output, callback
from .visualize import *
import dash_bootstrap_components as dbc
from pages.style import PADDING_STYLE
import plotly.express as px
import pandas as pd
import numpy as np


TEXT_STYLE = {
    'textAlign':'center',
    'width': '70%',
    'margin': '0 auto',
    'background-color': 'AliceBlue',
    'color': 'Blue'
}

layout =html.Div([
            html.H1('Conflicting Viewpoints',style={'textAlign':'center'}),
            html.Div([
                html.H3("Identifying Conflict, Influence and Polarizing Views", className="display-6 text-center"),
                html.P(id='conflictprinter',className='fs-4 text-center'),
                html.Hr(),
            ]), 
            dbc.Card([
                html.H5("Controversy and Relevance of Comments by Topics", className="card-title"),
                html.P("Here we summarize topics, sentiments and relevance in one graph. Each point represents aggregates by Topics", className = 'card-subtitle'),
                html.Li("Controversy (y-axis) Scale(-4, 4): We calculated the controversy score by finding how much the sentiment of a post's comment deviates from the sentiment of the post itself. In this axis we aggregated these deviations by topic."),
                html.Li("Relevance (x-axis) Scale(0, 1): Relevance is determined as shown previously. This axis shows the average relevance of comments aggregated by Topics."),
                html.Li("Comment Count (size): The size indicates how many comments belong to that Topic."),
                html.P("NOTE: Positive or negative controversy shows in which polarity the comments conflicted with their posts. This means that comments were either more positive or negative with respect the post they respond to.", className = 'card-subtitle'),

                    dcc.Loading(children=[
                        dcc.Graph(id='viewpoints1'),
                    ])
                ], style=PADDING_STYLE),
            dbc.Card([
                html.H5("Trends in average Comment Sentiment and Relevance propagated in a discussion.", className="card-title"),
                html.P("These two graphs show how sentiment and relevance change in a discussion as more and more comments are added to a post. The scores are averaged over a rolling window of 5 comments to observe trends better. Posts in the dropdown are ordered by descending order of number of total comments.", className = 'card-subtitle'),
                html.P("Choose a post in the dropdown selector provided to observe comment trends.", style=TEXT_STYLE),

                dcc.Loading(children=[
                    html.Div(children=[
                        dcc.Dropdown(
                            id='post_selection'
                        ),
                    ], style={'width': '70%', 'margin': '0 auto'}),
                    dcc.Graph(id='viewpoints2'),
                    dcc.Graph(id='viewpoints3'),
                    # dcc.Graph(id='viewpoints4'),
                ])
                ], style=PADDING_STYLE),
        ])


@callback(
    Output('conflictprinter', 'children'),
    Output('viewpoints1', 'figure'),
    Input('session', 'data')
)
def update_graph(data):
    try:
        df = pd.DataFrame(data)
        subreddit = df.at[0, 'subreddit']

        # figure 1: 
        df['sentiment_diff'] = df['comment_sentiment'] - df['post_sentiment']

        fig1_df = df[['comment_topics', 'comment_relevance', 'sentiment_diff']].groupby('comment_topics', as_index=False).agg(['mean', 'size']).reset_index()
        fig1_df = fig1_df.droplevel(1, axis=1)
        cols = ['comment_topics', 'comment_relevance_mean', 'comment_relevance_size', 'sentiment_diff_mean', 'sentiment_diff_size']
        fig1_df.columns = cols
        fig1_df['comment_topics'] = fig1_df['comment_topics'].apply(lambda s: ' '.join(s.split('_')[1:]))
        controversy_relevance_plot = cv_plot('scatter', fig1_df[1:], x_col='comment_relevance_mean', y_col='sentiment_diff_mean', size='sentiment_diff_size', title='Conflicting Viewpoints in r/'+subreddit,
                                             hover_name='comment_topics', 
                                             labels={
                                                 "sentiment_diff_mean": "Average Controversy",
                                                 "comment_relevance_mean": "Average Comment Relevance",
                                                 "sentiment_diff_size": "Number of Comments"
                                             })

        return f'We used posts and comments sentiment scores as well as their relevance scores to identify conflicting viewpoints in r/{subreddit}.', controversy_relevance_plot
    except KeyError as e:
        print(e)
        return 'No data loaded! Go to Home Page first!', {}

@callback(
    Output('post_selection', 'options'),
    Output('post_selection', 'value'),
    Output('viewpoints2', 'figure'),
    Output('viewpoints3', 'figure'),
    Input('session', 'data'),
    Input('post_selection', 'value')
)
def update_graph_2(data, post_id):
    try:
        df = pd.DataFrame(data)
        subreddit = df.at[0, 'subreddit']

        post_id_list = df[['post_id', 'post_index', 'post_title']].groupby('post_id',as_index=False, sort=False).agg({'post_index': 'count', 'post_title': 'first'})
        post_id_list = post_id_list[post_id_list['post_index'] > 9].sort_values(by=['post_index'], ascending=False).reset_index(drop=True)

        # figure 2
        if post_id is None:
            post_id_here = post_id_list.at[0, 'post_id']
            post_title = post_id_list.at[0, 'post_title']
        else:
            # post_id_here = post_id
            post_title = post_id
            post_id_here = post_id_list[post_id_list['post_title'] == post_id].iloc[0]['post_id']

        sent_df = df[df['post_id'] == post_id_here].sort_values('comment_created', ascending=True)

        ### Sentiment Plot
        sent_df['rolling_sent'] = sent_df['comment_sentiment'].rolling(5).mean()
        sentiment_avgs = sent_df['rolling_sent'].tolist()
        sentiment_avgs.insert(0, np.nan)
        comment_series_1_plot = px.line(sentiment_avgs, labels={
                     "index": "Number of Comments",
                     "value": "Rolling Average Comment Sentiment (5 Comments)",
                     "variable": "Rolling Average Comment Sentiment (5 Comments)"
                 }, title='Sentiment in Post:"'+post_title + '" - r/' + subreddit)
        comment_series_1_plot.update_layout(showlegend=False)

        ### Relevance Plot
        sent_df['rolling_rel'] = sent_df['comment_relevance'].rolling(5).mean()
        rel_avgs = sent_df['rolling_rel'].tolist()
        rel_avgs.insert(0, np.nan)
        comment_series_2_plot = px.line(rel_avgs, labels={
                     "index": "Number of Comments",
                     "value": "Rolling Average Comment Relevance (5 Comments)",
                     "variable": "Rolling Average Comment Relevance (5 Comments)"
                 }, title='Relevance in Post:"'+post_title + '" - r/' + subreddit)
        comment_series_2_plot.update_layout(showlegend=False)

        ### Controversy Plot
        # sent_df['sentiment_diff'] = sent_df['comment_sentiment'] - sent_df['post_sentiment']
        # sent_df['rolling_diff'] = sent_df['sentiment_diff'].rolling(5).mean()
        # diff_avgs = sent_df['rolling_diff'].tolist()
        # diff_avgs.insert(0, np.nan)
        # comment_series_3_plot = px.line(diff_avgs, labels={
        #              "index": "Number of Comments",
        #              "value": "Rolling Average Comment Controversy (5 Comments)",
        #              "variable": "Rolling Average Comment Controversy (5 Comments)"
        #          }, title=post_title + ' - ' + subreddit)
        # comment_series_3_plot.update_layout(showlegend=False)

        return post_id_list['post_title'], post_title, comment_series_1_plot, comment_series_2_plot
    except KeyError as e:
        print(e)
        return [], '', {}, {}
