from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from process.load_frames import getSummary
import plotly.graph_objs as go
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
colors = {
        'background' : '#FFFFFF',
        'text':'#7FDBFF'
    }
def Summaryreturns(summary_df):
    app = DjangoDash('returnsboard',external_stylesheets=external_stylesheets)
    trace_1 = go.Scatter(x = summary_df.index,
                        y = summary_df['Abs Return'],
                        name = 'Returns',
                        )

    data = [trace_1]

    layout = dict(title = 'Returns Chart',
                    showlegend = True,
                    plot_bgcolor = colors['background'],
                    paper_bgcolor = colors['background'],
                )
    font = dict(color = colors['text'])

    fig = dict(data = data, layout = layout, font = font)



    app.layout = html.Div(style = {'backgroundColor':colors['background']} ,
                        children=[
                            html.H1(children='Portfolio Returns Chart',style = {'textAlign':'center','color':colors['text']}),
                                    dcc.Graph(
                                        id='main-returns-graph',
                                        figure= fig
                                            )
                                ]
                        )

def Unitsreturns(value_dictionary):
    items = [k for k in value_dictionary]
    maxitems = len(items)


    subapp = DjangoDash('returns_all',external_stylesheets=external_stylesheets)
    data = []
    for i in items:
    	df = value_dictionary[i][0]
    	data.append(go.Scatter( x = df.index,
    							y = df['Abs Return'],
    							name = i,
    					)
    				)

    layout = dict(title = '',
                     showlegend = True,
                     plot_bgcolor = colors['background'],
                     paper_bgcolor = colors['background'],
                 )
    font = dict(color = colors['text'])
    fig = dict(data = data, layout = layout, font = font)
    subapp.layout = html.Div(style = {'backgroundColor':colors['background']} ,
                         children=[
                             html.H1(children='All Returns Comparison Chart',style = {'textAlign':'center','color':colors['text']}),
                                     dcc.Graph(
                                         id='returns-graph',
                                         figure= fig
                                             )
                                 ]
                         )

    # for i in items:
    #     shortname = 'returns_'+value_dictionary[i][1]
    #     df = value_dictionary[i][0]
    #     subapp = DjangoDash(shortname,external_stylesheets=external_stylesheets)
    #     subtrace_1 = go.Scatter(x = df.index,
    #                     y = df['Abs Return'],
    #                     name = 'Returns',
    #                     )
    #     data = [subtrace_1]

    #     layout = dict(title = 'Returns Summary Chart',
    #                 showlegend = True,
    #                 plot_bgcolor = colors['background'],
    #                 paper_bgcolor = colors['background'],
    #             )
    #     font = dict(color = colors['text'])

    #     fig = dict(data = data, layout = layout, font = font)

    #     subapp.layout = html.Div(style = {'backgroundColor':colors['background']} ,
    #                     children=[
    #                         html.H1(children=i,style = {'textAlign':'center','color':colors['text']}),
    #                                 dcc.Graph(
    #                                     id='returns-graph',
    #                                     figure= fig
    #                                         )
    #                             ]
    #                     )

if __name__ == '__main__':
    summary_df,value_dictionary = getSummary()

    Summaryreturns(summary_df)
    Unitsreturns(value_dictionary)
