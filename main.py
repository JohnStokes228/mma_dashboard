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
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import plotly.express as px
import time
from typing import List, Tuple, Dict
import statsmodels.api as sm
import itertools
from scipy.stats import chi2_contingency
import numpy as np

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
                              {'label': 'losses', 'value': 'losses'}],
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

        html.H2('chi squared independence test run on lowess regression lines results:'),
        dash_table.DataTable(id='chi2_test_results'),

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


@app.callback(
    [Output(component_id='chi2_test_results', component_property='data'),
     Output(component_id='chi2_test_results', component_property='columns')],
    [Input(component_id='style_select', component_property='value'),
     Input(component_id='x_var', component_property='value'),
     Input(component_id='y_var', component_property='value')]
)
def line_independence_test(
    option: List[str],
    x_var: str,
    y_var: str,
) -> Tuple[Dict[str, str], List[str]]:
    """Test whether the difference between the groups on the variables describe is significant.

    Parameters
    ----------
    option : chosen styles.
    x_var : the value of the x axis.
    y_var : the value of the y axis.
    """
    container = 'computing independance test for {} measured on variables {} and {}'.format(option, x_var, y_var)
    logger.info(container)

    df = pd.read_csv('data/per_fighter_recent.csv')
    lowess_dict = {}

    for opt in option:
        df_reduced = df[df['primary_discipline'] == opt]
        lowess_dict[opt] = pd.DataFrame(sm.nonparametric.lowess(df_reduced[y_var], df_reduced[x_var]))
        lowess_dict[opt]['discipline'] = opt

    lowess_df = pd.concat(lowess_dict)

    lowess_df['binned_x'] = pd.cut(lowess_df[0], 15)
    lowess_df = lowess_df.groupby(['binned_x', 'discipline']).mean().reset_index()
    lowess_df.sort_values(by=['discipline', 'binned_x'], inplace=True)
    lowess_df.columns = ['binned_x', 'discipline', 'x', 'y']
    lowess_df = lowess_df.pivot(columns='binned_x', index='discipline', values='y')

    pairs = list(itertools.combinations_with_replacement(option, 2))
    results = []
    for pair in pairs:
        prob_cont = lowess_df[lowess_df.index.isin(pair)].copy()
        prob_cont.dropna(axis=1, inplace=True)
        try:
            chi2_results = chi2_contingency(prob_cont)

            results.append((pair[0], pair[1], chi2_results[1], chi2_results[2]))
        except ValueError:
            logger.warning('at least one of {} do not have a lowess regression curve'.format(pair))

    results = pd.DataFrame(results)
    results.columns = ['discipline1', 'discipline2', 'p_val', 'dof']
    results['1_perc_sig'] = np.where(results['p_val'] <= 0.01, 1, 0)
    results['5_perc_sig'] = np.where(results['p_val'] <= 0.05, 1, 0)
    results['10_perc_sig'] = np.where(results['p_val'] <= 0.1, 1, 0)

    return results.to_dict(orient='records'), [{'name': col, 'id': col} for col in results.columns]


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
    main(acquisition=False)
