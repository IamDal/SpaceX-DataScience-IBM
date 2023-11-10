# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.io as pio

# Set plot template
pio.templates.default = "plotly_white"

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites = spacex_df.groupby(['Launch Site'],as_index=False)['Flight Number'].count()
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(style={'backgroundColor': '#F0F0F0'},
                        children=[html.H1('SpaceX Launch Records Dashboard',
                            style={'textAlign': 'center', 'color': '#503D36',
                            'font-size': 40,'background-color': 'rgb(255 255 255)'}),

                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options = [
                                                {'label':'All Launch Sites', 'value':'All'},
                                                *[{'label': f'Launch Site : {i}', 'value': f'{i}'} for i in launch_sites['Launch Site']],
                                            ],
                                            value = 'All',
                                            placeholder='Enter Launch Site',
                                            searchable=True
                                ),
                                html.Br(style={'background-color': 'rgb(255 255 255)'}),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart'),style={'background-color': 'rgb(255 255 255)'}),
                                html.Br(),

                                html.P("Payload range (Kg):",style={'textAlign': 'center','font-size': 20,'background-color': 'rgb(255 255 255)'}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,max=10000,step=1000,
                                                marks={i:f'{i}' for i in range(0,10000,1000)},
                                                value=[min_payload,max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'),style={'background-color': 'rgb(255 255 255)'}),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id = 'success-pie-chart',component_property = 'figure'),
              Input(component_id = 'site-dropdown',component_property = 'value'))
                
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby(['Launch Site'],as_index=False)['class'].sum()
    if entered_site == 'All':
        fig = px.pie(
                filtered_df,
                values='class', 
                names = 'Launch Site'
                )
        fig.update_layout(
        title={
            'text': "Successful Launches by Location",
            'y':.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        return fig
    else:
        filtered_df = spacex_df.loc[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df.groupby(['class'],as_index=False)['Launch Site'].count()
        fig = px.pie(
                filtered_df,
                values='Launch Site', 
                names = ['Failure','Success'], 
                title = 'Total Succesful launches for ' + entered_site                
                )
        fig.update_traces(textinfo='value')
        fig.update_layout(
        title={
            #'text': "Successful Launches by Location",
            'y':.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id = 'success-payload-scatter-chart',component_property = 'figure'),
                [Input(component_id = 'site-dropdown',component_property = 'value'),
                Input(component_id = 'payload-slider',component_property = 'value')])

def get_scatter_plot(site_name,payload):
    filtered_df = spacex_df.loc[(spacex_df['Payload Mass (kg)'] > payload[0]) & (spacex_df['Payload Mass (kg)'] < payload[1])]
    if site_name == 'All':
        fig1 = px.scatter(
                filtered_df,
                x='Payload Mass (kg)',
                y='class',
                color = 'Booster Version Category',
                size='Payload Mass (kg)'
                )
        return fig1
    else:
        site_payload = filtered_df.loc[filtered_df['Launch Site'] == site_name]
        fig1 = px.scatter(
                site_payload,
                x='Payload Mass (kg)',
                y='class',
                color = 'Booster Version Category',
                size='Payload Mass (kg)'
                )
        return fig1

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
