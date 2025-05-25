# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites=spacex_df[["Launch Site"]].drop_duplicates().values
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                    [{'label': i, 'value': i} for i in launch_sites],
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                marks={0: '0',
                                2500: '2500',
                                5000:'5000',
                                7500:'7500',
                                10000:'10000'},
                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        data = filtered_df[filtered_df["class"]==1].groupby("Launch Site").value_counts().reset_index()
        fig = px.pie(data, values='count', 
        names='Launch Site', 
        title='Total Success Launches By Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        data =  filtered_df[filtered_df["Launch Site"]==entered_site[0]]["class"].value_counts().reset_index()
        fig = px.pie(data, values='count', 
        names='class', 
        title='Total Success Launches site '+entered_site[0])
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart',component_property= 'figure'),
    [
        Input(component_id='site-dropdown',component_property= 'value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    # payload_range es una lista [min_payload, max_payload]
    low, high = payload_range

    # Filtrar el DataFrame según el rango de payload
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site == 'ALL':
        # Mostrar todos los sitios sin filtrar por site
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title='Payload vs Outcome for All Sites',
            labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
        )
        return fig

    else:
        # Filtrar por sitio seleccionado
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == selected_site]

        fig = px.scatter(
            filtered_site_df, 
            x='Payload Mass (kg)', 
            y='class',
            color='Booster Version Category',
            title=f'Payload vs Outcome for Site {selected_site}',
            labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
        )
        return fig


# Run the app
if __name__ == '__main__':
    app.run()
