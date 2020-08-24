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
        'background' : '#111111',
        'text':'#7FDBFF'
        }
def Summaryboard(summary_df):
    #summary_df = load_frames.summary_df
    app = DjangoDash('board',external_stylesheets=external_stylesheets)

    trace_1 = go.Scatter(x = summary_df.index,
                        y = summary_df['Overall Invested'],
                        name = 'Invested Amount',
                        )
    trace_2 = go.Scatter(x = summary_df.index,
                        y = summary_df['Portfolio Value'],
                        name = 'Investment Value',
                        )

    data = [trace_1,trace_2]

    layout = dict(title = 'Portfolio Chart',
                    showlegend = True,
                    plot_bgcolor = colors['background'],
                    paper_bgcolor = colors['background'],
                )
    font = dict(color = colors['text'])

    fig = dict(data = data, layout = layout, font = font)



    app.layout = html.Div(style = {'backgroundColor':colors['background']} ,
                        children=[
                            html.H1(children='Portfolio Summary Chart',style = {'textAlign':'center','color':colors['text']}),

                            # html.Div(children='''
                            #                 Dash: A web application framework for Python.
                            #                 Equity Investments summary graph
                            #                     ''',
                            #         style = {'textAlign':'center','color':colors['text']} ),

                                    dcc.Graph(
                                        id='main-graph',
                                        figure= fig
                                            )
                                ]
                        )

def Unitsboard(value_dictionary):
    #value_dictionary = load_frames.value_dictionary
    items = [k for k in value_dictionary]
    maxitems = len(items)

    for i in items:
        shortname = 'board_'+value_dictionary[i][1]
        df = value_dictionary[i][0]
        subapp = DjangoDash(shortname,external_stylesheets=external_stylesheets)
        subtrace_1 = go.Scatter(x = df.index,
                        y = df['Total Investment'],
                        name = 'Invested Amount',
                        )
        subtrace_2 = go.Scatter(x = df.index,
                        y = df['Total Value'],
                        name = 'Investment Value',
                        )

        data = [subtrace_1,subtrace_2]

        layout = dict(title = 'Summary Chart',
                    showlegend = True,
                    plot_bgcolor = colors['background'],
                    paper_bgcolor = colors['background'],
                )
        font = dict(color = colors['text'])

        fig = dict(data = data, layout = layout, font = font)

        subapp.layout = html.Div(style = {'backgroundColor':colors['background']} ,
                        children=[
                            html.H1(children=i,style = {'textAlign':'center','color':colors['text']}),

                            # html.Div(children='''
                            #                 Dash: A web application framework for Python.
                            #                 Equity Investments summary graph
                            #                     ''',
                            #         style = {'textAlign':'center','color':colors['text']} ),

                                    dcc.Graph(
                                        id='example-graph',
                                        figure= fig
                                            )
                                ]
                        )


    # rowindex = 1
    #     app2 = DjangoDash('board-2',external_stylesheets=external_stylesheets)
    #     subfigs = make_subplots(rows=maxitems, cols=1)
    #     df = value_dictionary[i][0]
    #     subfigs.append_trace(go.Scatter(
    #                             x = df.index,
    #                             y = df['Total Investment'],
    #                             name = i,
    #                             ), row=rowindex, col=1)
    #     rowindex += 1

    # subfigs.update_layout(layout)

    # #figi = dict(data = datai, layout = layout, font = font)



    # app2.layout = html.Div(style = {'backgroundColor':colors['background']} ,
    #                     children=[
    #                         html.H1(children='individual-graph Summary Chart',style = {'textAlign':'center','color':colors['text']}),

    #                                 dcc.Graph(
    #                                     id='individual-graph',
    #                                     figure= subfigs
    #                                         )
    #                             ]
    #                     )
    # @app.callback(
    #     Output(component_id='mydivision',component_property = 'children'),
    #     [Input(component_id = 'idslider',component_property = 'value')]
    #     )
    # def myfunctiondef(inpvalue):
    #     return 'Your magic input was "{}"'.format(inpvalue)

    # if __name__ == '__main__':
    #     app.run_server(host = '127.0.0.1',port = '8000',debug=True)


if __name__ == '__main__':
    summary_df,value_dictionary = getSummary()

    Summaryboard(summary_df)
    Unitsboard(value_dictionary)






