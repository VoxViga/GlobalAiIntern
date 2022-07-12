# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 01:24:56 2022

@author: hweij
"""

import numpy as np
import pandas as pd
import yfinance as yf
import time
import dash
import pymongo
import multiprocessing

from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from datetime import datetime, date
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pymongo
import dns
import json
import dash_bootstrap_components as dbc
import plotly
from plotly.offline import plot
import random

tickers = ['TSLA', 'AAPL', 'MSFT', 'AMZN', 'SPY']
stocks = yf.download(tickers, '2017-01-01', '2022-01-01')['Adj Close']


stocks.to_csv('historical_data.csv')

df1 = pd.read_csv('historical_data.csv', index_col=0)

last_day_price = yf.download(tickers, '2022-01-02', date.today())['Adj Close']

newdf = pd.concat([stocks, last_day_price])

newdf.to_csv('historical_data.csv')

#Connect MongoDB using pymongo
client = pymongo.MongoClient("mongodb+srv://voxviga:Vigahwj960303@cluster0.qie7n.mongodb.net/?retryWrites=true&w=majority")

db = client['GlobalAI']

col = db["5 year historical stock data"]
df2 = pd.read_csv('historical_data.csv')
df2_dict = df2.to_dict(orient='records')
col.insert_many(df2_dict)

def calc_stats(df):
    for i in df:
        df[i+'returns'] = df[i].pct_change()
        df[i+'stddev'] = df[i].std()
        df[i+'momentum'] = df[i]/df[i].shift(1)
        df[i+'differences'] = df[i].diff()
        df[i+'_30 days MA'] = df[i].rolling(window=30).mean()

# get the normal time
normaltimedf = newdf.copy()

st = time.time()
calc_stats(normaltimedf)
et = time.time()
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')

app = dash.Dash()

app.layout=html.Div([
    dcc.Input(id='my-id',value='Dash App',type='text'),
    html.Div(id='my-div')
])

server=app.server

colors = {     
     'background': '#111111',     
     'text': '#7FDBFF' } 

app.layout = html.Div([
    html.Br(),
    html.Br(),
    #header and logo
    html.H1('Stock Statistics Dashboard',
            style={'margin-top': 10, 'margin-left': 15, 'color': colors['background']}
    ),
        html.Img(
           src='https://images.squarespace-cdn.com/content/5c036cd54eddec1d4ff1c1eb/1557908564936-YSBRPFCGYV2CE43OHI7F/GlobalAI_logo.jpg?content-type=image%2Fpng',
           style={
               'height':'11%',
               'width':'11%',
               'float':'righttop',
               'position':'relative',
               'margin-top':11,
               'margin-right':10,
           },
           className='two columns'),

    html.Div(style={'backgroundColor': colors['text']}, children=[
        
    html.H4(
        children='Stock Close Price',
        style={
            'textAlign': 'center',
            'color': colors['background']
        }
    ),
    
    dcc.Graph(
        id='graph-1',
        figure={
            'data': [
                {'x': normaltimedf.index, 'y': normaltimedf['AAPL'], 'type': 'line', 'name': 'AAPL'},
                {'x': normaltimedf.index, 'y': normaltimedf['TSLA'], 'type': 'line', 'name': 'TSLA'},
                {'x': normaltimedf.index, 'y': normaltimedf['MSFT'], 'type': 'line', 'name': 'MSFT'},
                {'x': normaltimedf.index, 'y': normaltimedf['AMZN'], 'type': 'line', 'name': 'MSCI'},
                {'x': normaltimedf.index, 'y': normaltimedf['SPY'], 'type': 'line', 'name': 'SPY'},
            ],
            'layout': {
                'plot_bgcolor': colors['text'],
                'paper_bgcolor': colors['text'],
                'font': {
                    'color': colors['background']
                }
            }
        }
    ),
    
    html.H4(
        children='Stock Returns',
        style={
            'textAlign': 'center',
            'color': colors['background']
        }
    ),
    
    dcc.Graph(
        id='graph-2',
        figure={
            'data': [
                {'x': normaltimedf.index, 'y': normaltimedf['AAPLreturns'], 'type': 'line', 'name': 'AAPL'},
                {'x': normaltimedf.index, 'y': normaltimedf['TSLAreturns'], 'type': 'line', 'name': 'TSLA'},
                {'x': normaltimedf.index, 'y': normaltimedf['MSFTreturns'], 'type': 'line', 'name': 'MSFT'},
                {'x': normaltimedf.index, 'y': normaltimedf['AMZNreturns'], 'type': 'line', 'name': 'MSCI'},
                {'x': normaltimedf.index, 'y': normaltimedf['SPYreturns'], 'type': 'line', 'name': 'SPY'},
            ],
            'layout': {
                'plot_bgcolor': colors['text'],
                'paper_bgcolor': colors['text'],
                'font': {
                    'color': colors['background']
                }
            }
        }
    ),
    
        
    html.H4(
        children='Stock Stddev',
        style={
            'textAlign': 'center',
            'color': colors['background']
        }
    ),
    
    dcc.Graph(
        id='graph-3',
        figure={
            'data': [
                {'x': ['TSLA', 'AAPL', 'MSFT', 'AMZN', 'SPY'], 
                 'y': [normaltimedf['AAPLstddev'][0], normaltimedf['TSLAstddev'][0], normaltimedf['MSFTstddev'][0], 
                       normaltimedf['AMZNstddev'][0], normaltimedf['SPYstddev'][0]],'type': 'bar', 'name': 'AAPL'}
            ],
            'layout': {
                'plot_bgcolor': colors['text'],
                'paper_bgcolor': colors['text'],
                'font': {
                    'color': colors['background']
                }
            }
        }
    ),
        
    html.H4(
        children='Stock Momentum',
        style={
            'textAlign': 'center',
            'color': colors['background']
        }
    ),
    
    dcc.Graph(
        id='graph-4',
        figure={
            'data': [
                {'x': normaltimedf.index, 'y': normaltimedf['AAPLmomentum'], 'type': 'line', 'name': 'AAPL'},
                {'x': normaltimedf.index, 'y': normaltimedf['TSLAmomentum'], 'type': 'line', 'name': 'TSLA'},
                {'x': normaltimedf.index, 'y': normaltimedf['MSFTmomentum'], 'type': 'line', 'name': 'MSFT'},
                {'x': normaltimedf.index, 'y': normaltimedf['AMZNmomentum'], 'type': 'line', 'name': 'MSCI'},
                {'x': normaltimedf.index, 'y': normaltimedf['SPYmomentum'], 'type': 'line', 'name': 'SPY'},
            ],
            'layout': {
                'plot_bgcolor': colors['text'],
                'paper_bgcolor': colors['text'],
                'font': {
                    'color': colors['background']
                }
            }
        }
    ),

    
    html.H4(
        children='Stock 30 days MA',
        style={
            'textAlign': 'center',
            'color': colors['background']
        }
    ),
    
    dcc.Graph(
        id='graph-5',
        figure={
            'data': [
                {'x': normaltimedf.index, 'y': normaltimedf['AAPL_30 days MA'], 'type': 'line', 'name': 'AAPL'},
                {'x': normaltimedf.index, 'y': normaltimedf['TSLA_30 days MA'], 'type': 'line', 'name': 'TSLA'},
                {'x': normaltimedf.index, 'y': normaltimedf['MSFT_30 days MA'], 'type': 'line', 'name': 'MSFT'},
                {'x': normaltimedf.index, 'y': normaltimedf['AMZN_30 days MA'], 'type': 'line', 'name': 'MSCI'},
                {'x': normaltimedf.index, 'y': normaltimedf['SPY_30 days MA'], 'type': 'line', 'name': 'SPY'},
            ],
            'layout': {
                'plot_bgcolor': colors['text'],
                'paper_bgcolor': colors['text'],
                'font': {
                    'color': colors['background']
                }
            }
        }
    )
    
    ])
    ])
    
if __name__ == '__main__':
    app.run_server()



































