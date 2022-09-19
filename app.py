# Code source: https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/
from pydoc import classname
import dash
from dash import html, dcc, callback, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
from pages.sas_key import get_df, get_df_description
from pages.visualize import *
import pandas as pd
import json
from pages import relevance_page, facts_page, topicmodeling_page, sentimentanalysis_page, conflictingviewpoints_page

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css'],
                meta_tags=[
                  {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ], 
                suppress_callback_exceptions=True)
app.title = "BEReddiT"

server = app.server

# Read the list of available subreddits
file1 = open("pages/subreddit_list.txt", "r")
subreddits = file1.readlines()
subreddits = list(set(map(lambda item: item.replace('\n', ''), subreddits)))
subreddits.sort(key=str.lower)
file1.close()

# styling the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# padding for the page content
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

# Center of Div
CENTER_STYLE = {
    'width': '70%',
    'margin': '0 auto',
}

TEXT_STYLE = {
    'textAlign':'center',
    'width': '70%',
    'margin': '0 auto',
    'background-color': 'AliceBlue',
    'color': 'Blue'
}


with open('pages/fig.json', 'r') as f:
    subreddit_fig = json.load(f)

sidebar = html.Div(
    [
        html.Img(src='/assets/bereddit-logo.png', style={'width':'100%'}),
        html.P(
            "BEReddiT", className="display-5 text-center"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Subreddit", href="/facts", active="exact"),
                dbc.NavLink("Topic Modeling", href="/topicmodeling", active="exact"),
                dbc.NavLink("Sentiment Analysis", href="/sentimentanalysis", active="exact"),
                dbc.NavLink("Relevance Score", href="/relevance", active="exact"),
                dbc.NavLink("Conflicting Viewpoints", href="/conflictingviewpoints", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Loading(children=[dcc.Store(id='session', storage_type='memory')], fullscreen=True),
    dcc.Loading(children=[dcc.Store(id='session2', storage_type='memory')], fullscreen=True),
    sidebar,
    content
])


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    try:
        ### Home Page
        if pathname == "/":
            # Can add more items to the list, for more content in homepage.
            return  html.Div([

                        # Welcome Header
                        html.H1('The Topic-Sentiment and Relevance System | TSAR', style={'textAlign':'center'}),
                        html.Hr(),
                        # Introduction Paragraph
                        html.Div([
                            html.H4('Our aim is to find ways to identify and discover conflicting viewpoints in online social forums/discussions (subreddits) using topic modeling, sentiment analysis and by measuring relevance of material within these discussions.', className="display-6 text-center"),
                            html.Hr(),
                           ]),
                        html.Div([
                            dbc.Card(
                                dbc.CardBody(
                                        [
                                            html.H3('Pick a SubReddit to Analyze (Use the plot below for guidance!)', className="card-title text-center"),
                                            html.H4(id="homesubredditprinter", className="card-subtitle", style=TEXT_STYLE),
                                            html.Div([
                                                dcc.Dropdown(
                                                    subreddits,
                                                    "computerscience",
                                                    id='data',
                                                )
                                            ], style=CENTER_STYLE, className='card-text'),
                                        ]),
                                    )
                        ]),
                        html.Hr(),
                        ### Figure for subreddit scatter plot
                        dcc.Loading(children=[
                            html.P("The Map of Reddit gives you a bird's-eye view of the results of the TSAR system on multiple subreddits' comments. It's designed to help you choose interesting subreddits to look at with TSAR. Each point is a subreddit (hover over points to see). It shows two important metrics that we devised: Comment Controversy - showing average conflict in discussions by either positively or negatively affecting the sentiments of the discussion; and Comment Relevance - showing how relevant comments are to their posts.", className = 'fs-3'),
                            dcc.Graph(figure=subreddit_fig),
                        ]),
                        html.Div([

                            html.H6('What is the TSAR System?', className = 'display-6'),
                            html.P('The TSAR System is a complex data engineering pipeline that utilizes Natural Language Processing to analyze internet forum discussions using dedicated APIs depending on the source of data.', className = 'fs-3'),
                            html.P('Here, we use Reddit APIs to access data from various subreddits.', className = 'fs-3'),
                            html.P('TSAR is powered by BERT word embeddings and the system consists of multiple components that you will see in the various pages of this application, which are as follows:', className = 'fs-3'),
                            html.Li('Topic Modeling - To find topics in Posts and Comments', className = 'fs-3'),
                            html.Li('Sentiment Analysis - To find sentiments of Posts and Comments.', className = 'fs-3'),
                            html.Li('Relevance Score - To observe the relevance of Comments with respect to their Posts.', className = 'fs-3'),
                            html.Li('Conflicting Viewpoints - To observe the results of TSAR on the selected subreddit.', className = 'fs-3'),
                        ]),
                        html.Hr(),
                        html.Div([
                            html.H6('Motivation', className = 'display-6'),
                            html.P('With the advent of popular social media or forums and their power in swaying decision-making due to sensationalization of various topics of discussion, it seems to be reasonable to look for polarizing discussion on such platforms. Reddit.com is one of the most popular websites used to discuss and share ideas with like-minded users due to its well-organized structure. Reddit consists of a database of forums referred to as “subreddits” which contain posts about specific topics. Each subreddit has at least one “moderator” who is in charge of the content that is posted on their subreddit. With over 430 million monthly active users and >100,000 active subreddits, Reddit has provided people with a platform to express (potentially radical) ideas and debate on various levels from mundane to extreme topics of discussion.', className = 'fs-3'),
                            html.P('Bias in opinion is the driving force behind extreme opposition from different sides in a polarizing discussion. This extremism can lead to conflict with no side leaning into a compromising state of resolution. Oftentimes when a debate reaches a level of acute polarization, bias sways different people to incline to different perspectives without giving much thought to the holistic viewpoint. This encouraged us to pursue the idea of understanding, observing and finding ways to uncover these conflicting viewpoints to obtain balanced information from a discussion at hand.', className = 'fs-3'),
                            html.P('We aim to understand how we can use current approaches to natural language processing to understand the semantics of debate and biased discussion by uncovering conflicting viewpoints. On a social level, we aim to create an impact in such forums to enable balanced debates on varying perspectives to show respect to all views with reasonable arguments.', className = 'fs-3')

                        ]),
####TODO: show technical details of implementation

            ])
        
        ### Quick Facts Page
        elif pathname == "/facts":
            return facts_page.layout

        ### Relevance Page
        elif pathname == "/relevance":
            return relevance_page.layout

        ### Topic Modeling Page
        elif pathname == "/topicmodeling":
            return topicmodeling_page.layout

        ### Sentiment Page
        elif pathname == "/sentimentanalysis":
            return sentimentanalysis_page.layout

        ### Conflicting Viewpoints Page
        elif pathname == "/conflictingviewpoints":
            return conflictingviewpoints_page.layout

    except ValueError as e:
        print(e)
        return html.H1('No data loaded. Head to Home Page First!', style={'textAlign':'center'})
    except NameError as e:
        print(e)
        return html.H1('No data loaded. Head to Home Page First!', style={'textAlign':'center'})


    ### 404 Page
    # If the user tries to reach a different page, return a 404 message
    return html.H1('404: Page Not Found', style={'textAlign':'center'})

### USED TO UPDATE THE DF FROM HOME PAGE
@app.callback(
    Output('session', 'data'),
    Output('session2', 'data'),
    Output('homesubredditprinter', 'children'),
    Input('data', 'value')
)
def update_df(value):
    # Load the data
    df = get_df(value)
    return df.to_dict("records"), value, f"Current Selection is r/{value}"


if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(debug=False)
