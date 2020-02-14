import dash
import dash_core_components as dcc
import dash_html_components as html

import colorlover as cl
import datetime as dt
import flask
import os
import pandas as pd
import time
import yfinance as yf

app = dash.Dash(
    __name__, 
    assets_external_scripts='https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
)
server = app.server

app.scripts.config.serve_locally = False


colorscale = cl.scales['9']['qual']['Paired']

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/dash-stock-ticker-demo.csv')

company_list = pd.read_csv('companylist.csv')
print(company_list)
company_list2 = pd.read_csv('companylist2.csv')
print(company_list2)

print("list1    " + company_list.Symbol.unique())
print(company_list.Symbol.unique())
print("list2     ")
print(company_list2.Symbol.unique())


#company_list = company_list.merge(company_list2, on='Symbol')

#company_list = pd.concat([company_list, company_list2], axis=1, sort=False)


company_list = pd.concat([company_list, company_list2], ignore_index=True, sort=False)
#company_list.append(company_list2, sort=False)
print(company_list)
print("googl     ")
print(company_list.loc[company_list['Symbol'] == "GOOGL"])
print("yhoo     ")
print(company_list.loc[company_list['Symbol'] == "YHOO"])

# print("----------")
# print("googl     ")
# print(result.loc[result['Symbol'] == "GOOGL"])
# print("yhoo     ")
# print(result.loc[result['Symbol'] == "YHOO"])


print(company_list.Symbol.unique())

app.layout = html.Div([
    html.Div([
        html.H2('Finance Explorer',
                style={'display': 'inline',
                       'float': 'left',
                       'font-size': '2.65em',
                       'margin-left': '7px',
                       'font-weight': 'bolder',
                       'font-family': 'Product Sans',
                       'color': "rgba(117, 117, 117, 0.95)",
                       'margin-top': '20px',
                       'margin-bottom': '0'
                       }),
        # html.Img(src='/static/img/sig2lead_black2.png',
        #
        #         style={
        #             'height': '100px',
        #             'float': 'right'
        #         },
        # ),
    ]),
    dcc.Dropdown(
        id='stock-ticker-input',
        options=[{'label': s[0], 'value': str(s[1])}
                 for s in zip(company_list.Symbol.unique(), company_list.Symbol.unique())],
        value=['YHOO', 'GOOGL'],
        multi=True
    ),
    html.Div(id='graphs')
], className="container")

def bbands(price, window_size=10, num_of_std=5):
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std  = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)
    return rolling_mean, upper_band, lower_band

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('stock-ticker-input', 'value')])
def update_graph(tickers):
    graphs = []

    if not tickers:
        graphs.append(html.H3(
            "Select a stock ticker.",
            style={'marginTop': 20, 'marginBottom': 20}
        ))
    else:
        for i, ticker in enumerate(tickers):

            dff = df[df['Stock'] == ticker]

            candlestick = {
                'x': dff['Date'],
                'open': dff['Open'],
                'high': dff['High'],
                'low': dff['Low'],
                'close': dff['Close'],
                'type': 'candlestick',
                'name': ticker,
                'legendgroup': ticker,
                'increasing': {'line': {'color': colorscale[0]}},
                'decreasing': {'line': {'color': colorscale[1]}}
            }
            bb_bands = bbands(dff.Close)
            bollinger_traces = [{
                'x': dff['Date'], 'y': y,
                'type': 'scatter', 'mode': 'lines',
                'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
                'hoverinfo': 'none',
                'legendgroup': ticker,
                'showlegend': True if i == 0 else False,
                'name': '{} - bollinger bands'.format(ticker)
            } for i, y in enumerate(bb_bands)]
            graphs.append(dcc.Graph(
                id=ticker,
                figure={
                    'data': [candlestick] + bollinger_traces,
                    'layout': {
                        'margin': {'b': 0, 'r': 10, 'l': 60, 't': 0},
                        'legend': {'x': 0}
                    }
                }
            ))

    return graphs


if __name__ == '__main__':

    # msft = yf.Ticker("MSFT")
    # print(msft)
    # print(msft.info)
    # print(msft.history(period="max"))
    app.run_server(debug=True)
