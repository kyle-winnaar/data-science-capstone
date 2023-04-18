# Import required libraries
import os
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Get working directory
path, _ = os.path.split(__file__)

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(os.path.join(path, 'spacex_launch_dash.csv'))
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites_df = spacex_df[['Launch Site']]
launch_sites_df = launch_sites_df.groupby(['Launch Site'], as_index=False).first()
num_launch_sites = launch_sites_df.shape[0]

launch_sites = [{'label': 'ALL LAUNCH SITES', 'value': 'ALL'}]
for row in range(num_launch_sites):
    launch_site = {'label': launch_sites_df['Launch Site'][row], 'value': launch_sites_df['Launch Site'][row]}
    launch_sites.append(launch_site)


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=launch_sites,
                                             value='ALL',
                                             placeholder='Select a launch site',
                                             searchable=True,
                                             style={'width': '80%','padding': '3px', 'font-size': '20px', 'text-align': 'center'}
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.H2("Payload range (kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=500,
                                                allowCross=False,
                                                tooltip={"placement": "bottom", "always_visible": True},
                                                marks={0: '0 kg',
                                                       2500: '2500 kg',
                                                       5000: '5000 kg',
                                                       7500: '7500 kg',
                                                       10000: '10000 kg'},
                                                value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ]
                                )

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # filtered_df = spacex_df
    if entered_site == 'ALL':
        data = spacex_df[spacex_df['class'] == 1]
        # data = data.groupby(['Launch Site', 'class'], as_index=False).count()
        fig = px.pie(data,
                     values='class',
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        data = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = data.groupby(['Launch Site', 'class'], as_index=False).count()
        fig = px.pie(data,
                     values='Flight Number',
                    #  names=['Failed', 'Success'],
                     names='class',
                     title=f'Total Launches for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, slider_range):
    if entered_site == 'ALL':
        data = spacex_df[(spacex_df['Payload Mass (kg)'] >= slider_range[0]) &
                         (spacex_df['Payload Mass (kg)'] <= slider_range[1])]
        fig = px.scatter(data,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Payload Mass vs Launch Outcome for all sites')
        return fig
    else:
        data = spacex_df[(spacex_df['Payload Mass (kg)'] >= slider_range[0]) &
                         (spacex_df['Payload Mass (kg)'] <= slider_range[1]) &
                         (spacex_df['Launch Site'] == entered_site)]
        fig = px.scatter(data,
                         x='Payload Mass (kg)',
                         y='class',
                         color='Booster Version Category',
                         title=f'Payload Mass vs Launch Outcome for {entered_site}')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()


    # Answers to specific questions:
    # 1. Which site has the largest successful launches?
    #   --> KSC LC-39-A (41.7 %, 10)

    # 2. Which site has the highest launch success rate?
    #   --> CCAFS SLC-40 (42.9 %, 3)

    # 3. Which payload range(s) has the highest launch success rate?
    #   --> (1900 kg, 3700 kg)

    # 4. Which payload range(s) has the lowest launch success rate?
    #   --> 

    # 5. Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest launch success rate?
    #   --> 
