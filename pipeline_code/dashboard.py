"""
Dashboard code will go in this file. bet you can hardly wait.
"""
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import plotly.express as px
import time
from typing import List, Tuple
from pipeline_code.logger_module import get_pipeline_logger


logger = get_pipeline_logger(__name__, filename=time.strftime('%d%m%y_%H%M%S'))
app = dash.Dash(__name__)


def get_dashapp_structure(app: dash.Dash) -> dash.Dash:
    """Gets the dash app object.

    Parameters
    ----------
    app : dash app.

    Returns
    -------
    Structured html for desired output.
    """
    logger.info('Constructing dashboard HTML')

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


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='poxy_graph', component_property='figure')],
    [Input(component_id='style_select', component_property='value')]
)
def update_poxy_graph(
    option: List[str],
) -> Tuple[str, px.scatter]:
    """Function to update output graph based on selected option.

    Parameters
    ----------
    option : chosen styles.
    df : The data for the poxy graph.
    """
    container = 'user selected the options: {}'.format(option)
    logger.info(container)

    df = pd.read_csv('../data/per_fighter_recent.csv')

    df_reduced = df[df['primary_discipline'].isin(option)]

    fig = px.scatter(data_frame=df_reduced,
                     x='tot_str_attempted_bout_mean',
                     y='sub_attempts_bout_mean',
                     color='primary_discipline',
                     marginal_y='violin'
    )

    return container, fig


def build_dashboard(app: dash.Dash) -> None:
    """Runs the dash code and constructs the dashboard.

    Parameters
    ----------
    app : dash app.
    """
    app = get_dashapp_structure(app)
    app.run_server(debug=True)


if __name__ == '__main__':
    build_dashboard(app)
