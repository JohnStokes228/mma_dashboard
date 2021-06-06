"""
Main script for dashboard project. pulls together and runs the various modules
"""
from pipeline_code import (
    acquire_data,
    per_fighter_pipeline,
    logger_module,
)
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import plotly.express as px
import time
from typing import List, Tuple

logger = logger_module.get_pipeline_logger(__name__, filename=time.strftime('%d%m%y_%H%M%S'))
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

        dcc.Dropdown(id='x_var',
                     options=[{'label': 'mean submissions attempted', 'value': 'sub_attempts_bout_mean'},
                              {'label': 'mean takedowns attempted', 'value': 'td_attempted_bout_mean'},
                              {'label': 'mean significant strikes attempted', 'value': 'sig_str_attempted_bout_mean'},
                              {'label': 'mean knockdowns', 'value': 'kd_bout_mean'},
                              {'label': 'mean total strikes attempted', 'value': 'tot_str_attempted_bout_mean'},
                              {'label': 'mean guard passes', 'value': 'pass_bout_mean'},
                              {'label': 'mean reversals', 'value': 'rev_bout_mean'},
                              {'label': 'mean takedowns landed', 'value': 'td_landed_bout_mean'},
                              {'label': 'mean significant strikes landed', 'value': 'sig_str_landed_bout_mean'},
                              {'label': 'mean knockdowns', 'value': 'kd_bout_mean'},
                              {'label': 'mean total strikes landed', 'value': 'tot_str_landed_bout_mean'},
                              {'label': 'mean significant strikes absorbed', 'value': 'sig_str_absorbed_bout_mean'},
                              {'label': 'mean takedown defence rate', 'value': 'td_defence_rate_bout_mean'},
                              {'label': 'wins', 'value': 'wins'},
                              {'label': 'wins', 'value': 'losses'}],
                     value='sub_attempts_bout_mean',
                     style={'display': 'block'}),

        dcc.Dropdown(id='y_var',
                     options=[{'label': 'mean submissions attempted', 'value': 'sub_attempts_bout_mean'},
                              {'label': 'mean takedowns attempted', 'value': 'td_attempted_bout_mean'},
                              {'label': 'mean significant strikes attempted', 'value': 'sig_str_attempted_bout_mean'},
                              {'label': 'mean knockdowns', 'value': 'kd_bout_mean'},
                              {'label': 'mean total strikes attempted', 'value': 'tot_str_attempted_bout_mean'},
                              {'label': 'mean guard passes', 'value': 'pass_bout_mean'},
                              {'label': 'mean reversals', 'value': 'rev_bout_mean'},
                              {'label': 'mean takedowns landed', 'value': 'td_landed_bout_mean'},
                              {'label': 'mean significant strikes landed', 'value': 'sig_str_landed_bout_mean'},
                              {'label': 'mean knockdowns', 'value': 'kd_bout_mean'},
                              {'label': 'mean total strikes landed', 'value': 'tot_str_landed_bout_mean'},
                              {'label': 'mean significant strikes absorbed', 'value': 'sig_str_absorbed_bout_mean'},
                              {'label': 'mean takedown defence rate', 'value': 'td_defence_rate_bout_mean'},
                              {'label': 'wins', 'value': 'wins'},
                              {'label': 'losses', 'value': 'losses'}],
                     value='td_attempted_bout_mean',
                     style={'display': 'block'}),

        html.Div(id='output_container', children=[]),
        html.Br(),

        dcc.Graph(id='poxy_graph', figure={}),
        html.Br(),

        dcc.Slider(id='sunburst_year',
                   min=2010,
                   max=2021,
                   value=2010,
                   marks={str(val): val for val in range(2010, 2022)},
                   step=None
                   ),
        dcc.Graph(id='sunburst_graph', figure={}),

        html.Div(id='output_container_2', children=[]),
        html.Br()
    ])

    return app


@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='poxy_graph', component_property='figure')],
    [Input(component_id='style_select', component_property='value'),
     Input(component_id='x_var', component_property='value'),
     Input(component_id='y_var', component_property='value')]
)
def update_poxy_graph(
    option: List[str],
    x_var: str,
    y_var: str,
) -> Tuple[str, px.scatter]:
    """Function to update output graph based on selected option.

    Parameters
    ----------
    option : chosen styles.
    x_var : the value of the x axis.
    y_var : the value of the y axis.
    """
    container = 'user selected the options: {}, on the axes {}, {}'.format(option, x_var, y_var)
    logger.info(container)

    df = pd.read_csv('data/per_fighter_recent.csv')

    df_reduced = df[df['primary_discipline'].isin(option)]

    fig = px.scatter(
        data_frame=df_reduced,
        x=x_var,
        y=y_var,
        color='primary_discipline',
        marginal_y='violin',
        trendline='lowess',
        title='fight stats by primary discipline scatter plot'
    )

    return container, fig


@app.callback(
    [Output(component_id='sunburst_graph', component_property='figure'),
     Output(component_id='output_container_2', component_property='children')],
    [Input(component_id='sunburst_year', component_property='value')]
)
def update_sunburst_graph(
    year: str,
) -> Tuple[px.sunburst, str]:
    """Control the year displayed on the sunburst graph.

    Parameters
    ----------
    year : The year of data to be visualised.

    Returns
    -------
    Sunburst graph of chosen year
    """
    container = 'user selected the sunburst year: {}'.format(year)
    logger.info(container)

    df = pd.read_csv('data/complete_fight.csv')

    df_reduced = df[df['year'] == year]
    df_reduced = df_reduced.groupby(['continent', 'country', 'city']).count().reset_index()

    fig = px.sunburst(data_frame=df_reduced,
                      path=['continent', 'country', 'city'],
                      values='bout_id',
                      title='fights per region by year'
                      )

    return fig, container


def build_dashboard(app: dash.Dash) -> None:
    """Runs the dash code and constructs the dashboard.

    Parameters
    ----------
    app : dash app.
    """
    app = get_dashapp_structure(app)
    app.run_server(debug=False)


def main(
    acquisition: bool = True
) -> None:
    """Run the bloody thing.

    Parameters
    ----------
    acquisition : Set True to run the acquisition / data transformation modules.
    """
    logger.info('Beginning dashboard run')

    if acquisition:
        logger.info('USER SELECTED - acquire fresh data')
        acquire_data.acquire_data_main()
        per_fighter_pipeline.per_fighter_pipeline_main()
        logger.info('Completed data acquisition and transformation')

    build_dashboard(app)


if __name__ == '__main__':
    main(acquisition=True)
