from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from pages.style import PADDING_STYLE


layout =html.Div([
            html.H1('Topic Modeling',style={'textAlign':'center'}),
            html.Div([
                html.H3("What are people talking about here?", className="display-6 text-center"),
                html.P(id='topicsubredditprinter', className='fs-4 text-center'),
                html.Hr(),
            ]), 
            dbc.Card(style=PADDING_STYLE, children=[
                html.H5("List of Topics"),
                html.Div(className='row', children=[
                    dcc.Loading(children=[
                        ### Post Topic Table
                        html.Div(className="six columns", children=[
                            dash_table.DataTable(id="posttopicstable",
                                                 style_header={'font-weight': 'bold'},
                                                 fixed_rows={'headers': True},
                                                 style_cell={'font-family':'sans-serif', 'font-size': '14px', 'text-align': 'center'},
                                                 style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                                 style_table={'overflowY': 'scroll', 'height': '242px'})
                        ]),
                        ### Comment Topic Table
                        html.Div(className="six columns", children=[
                            dash_table.DataTable(id="commenttopicstable",
                                                 style_header={'font-weight': 'bold'},
                                                 fixed_rows={'headers': True},
                                                 style_cell={'font-family':'sans-serif', 'font-size': '14px', 'text-align': 'center'},
                                                 style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                                 style_table={'overflowY': 'scroll', 'height': '242px'})
                        ])
                    ]),
                ])
            ]),

            ### Post Topic Modeling
            dbc.Card([
                html.H5("Post Topic Modeling"),
                dcc.Loading(children=[
                    dcc.Graph(id='topic2'),
                ]),
            ], style=PADDING_STYLE),
            ### End Post Topic Modeling
            ### Comment Topic Modeling
            dbc.Card([
                html.H5("Comment Topic Modeling"),
                dcc.Loading(children=[
                    dcc.Graph(id='topic1'),
                ]),
            ], style=PADDING_STYLE),
            ### End Comment Topic Modeling
            
        ])

@callback(
    # Output('first', 'figure'),
    Output('topicsubredditprinter', 'children'),
    Output('topic1', 'figure'),
    Output('topic2', 'figure'),
    Output('posttopicstable', 'data'),
    Output('commenttopicstable', 'data'),
    Input('session', 'data')
)
def update_graph(data):
    try:
        df = pd.DataFrame(data)
        subreddit = df.at[0, 'subreddit']
        
        # Topic modeling for posts
        post_df = df[['post_topics', 'post_id']].groupby('post_topics', as_index=False).count()
        post_df = post_df[~post_df['post_topics'].str.startswith('-1')]
        post_df['post_topics'] = post_df['post_topics'].apply(lambda s: ' '.join(s.split('_')[1:]))
        post_topics_fig = px.bar(post_df[:15],
                                 x='post_topics',
                                 y='post_id',
                                 title='Important Topics For Posts',
                                 labels={'post_topics':'Topics', 'post_id':'Count (Number of Posts)'})
        post_topics_fig.update_xaxes(categoryorder='total descending')
        post_topics_fig.update_layout(showlegend=False)
        
        # Topic modeling for comments
        df.dropna(inplace=True, subset=['comment_topics'])
        df = df[~df['comment_topics'].str.startswith('-1')]
        df['comment_topics'] = df['comment_topics'].apply(lambda s: ' '.join(s.split('_')[1:]))
        comm_topics_fig = px.bar(df.comment_topics.value_counts()[:15],
                                 title='<b>Top 15</b> Important Topics For Comments',
                                 labels={'index':'Topics', 'value':'Count (Number of Comments)', 'variable':'Topics'})
        comm_topics_fig.update_layout(showlegend=False)
        
        # List of all topics
        list_of_post_topics = post_df['post_topics'].unique()
        list_of_comment_topics = df['comment_topics'].unique()
        list_of_post_topics = pd.DataFrame(list_of_post_topics, columns=['Post Topics']).sort_values(by=['Post Topics'])
        list_of_comment_topics = pd.DataFrame(list_of_comment_topics, columns=['Comment Topics']).sort_values(by=['Comment Topics'])

        return f'Here we can see what the most prominent topics of discussion are in current comments and posts of r/{subreddit}. Topics are listed as groups of words found to be most occuring together and most related within current discussions.', comm_topics_fig, post_topics_fig, list_of_post_topics.to_dict('records'), list_of_comment_topics.to_dict('records')
    except KeyError as e:
        print(e)
        return 'No data loaded! Go to Home Page first!', {}, {}, [], []
