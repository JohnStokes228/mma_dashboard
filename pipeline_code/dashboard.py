"""
Dashboard code will go in this file. bet you can hardly wait.
"""
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly
import time
from pipeline_code.logger_module import get_pipeline_logger


logger = get_pipeline_logger(__name__, filename=time.strftime('%d%m%y_%H%M%S'))


def get_dashapp_structure() -> dash.Dash:
    """Gets the dash app object.

    Returns
    -------
    Structured html for desired output.
    """
    logger.info('Constructing dashboard HTML')
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("MMA Dashboard Take 1", style={'text-align': 'center'}),

        dcc.Checklist(id='style_select',
                      options=[{'label': 'karateka', 'value': 'karate'},
                               {'label': 'jiu jitiero', 'value': 'jiu jitsu'},
                               {'label': 'mixed martial artists', 'value': 'mixed'},
                               {'label': 'judokas', 'value': 'judo'},
                               {'label': 'boxers', 'value': 'boxing'},
                               {'label': 'taekwondoins', 'value': 'taekwondo'},
                               {'label': 'kickboxers', 'value': 'kickboxing'},
                               {'label': 'wrestlers', 'value': 'wrestling'},
                               {'label': 'thai boxers', 'value': 'muay thai'},
                               {'label': 'sambo artists', 'value': 'sambo'},
                               {'label': 'kung fu disciples', 'value': 'kung fu'},
                               {'label': 'capoeira', 'value': 'capoeira'}],
                      value=['karate'],
                      labelStyle={'display': 'block'}),

        html.Div(id='output_container', children=[]),
        html.Br(),

        dcc.Graph(id='poxy_graph', figure={})
    ])

    return app


def build_dashboard() -> None:
    """Runs the dash code and constructs the dashboard.
    """
    app = get_dashapp_structure()
    app.run_server(debug=True)


if __name__ == '__main__':
    build_dashboard()