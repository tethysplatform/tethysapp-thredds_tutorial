from plotly import graph_objs as go
from netCDF4 import num2date


def generate_figure(time_series, dataset, variable):
    """
    Generate a figure from a netCDF4.Dataset.

    Args:
        time_series(netCDF4.Dataset): A time series NetCDF4 Dataset.
        dataset(str): The name of the time series dataset.
        variable(str): The name of the variable to plot.
    """
    figure_data = []
    figure_title = dataset

    column_name = variable.replace('_', ' ').title()

    yaxis_title = column_name
    series_name = column_name

    # Add units to yaxis title
    variable_units = time_series.variables[variable].units
    if variable_units:
        yaxis_title += f' ({variable_units})'

    # Extract needed arrays for plot from NetCDF4 Dataset
    variable_array = time_series.variables[variable][:].squeeze()
    time = time_series.variables['time']
    time_array = num2date(time[:].squeeze(), time.units)

    series_plot = go.Scatter(
        x=time_array,
        y=variable_array,
        name=series_name,
        mode='lines'
    )

    figure_data.append(series_plot)

    figure = {
        'data': figure_data,
        'layout': {
            'title': {
                'text': figure_title,
                'pad': {
                    'b': 5,
                },
            },
            'yaxis': {'title': yaxis_title},
            'legend': {
                'orientation': 'h'
            },
            'margin': {
                'l': 40,
                'r': 10,
                't': 80,
                'b': 10
            }
        }
    }

    return figure
