from urllib.parse import urlparse
from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import SelectInput
from .app import ThreddsTutorial as app
from django.http import HttpResponseNotAllowed, JsonResponse
from .thredds_methods import parse_datasets, get_layers_for_wms
import logging
import geojson
from datetime import datetime
from simplejson.errors import JSONDecodeError
from tethys_sdk.gizmos import SelectInput, PlotlyView
from .figure import generate_figure
from .thredds_methods import parse_datasets, get_layers_for_wms, extract_time_series_at_location


log = logging.getLogger(__name__)


@controller
def home(request):
    """
    Controller for the app home page.
    """
    catalog = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_engine=True)

    # Retrieve dataset options from the THREDDS service
    log.info('Retrieving Datasets...')
    datasets = parse_datasets(catalog)
    
    # Replace private url with public url
    # TODO: move into parse_datasets and replace as the initial datasets array is built
    public_endpoint = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_public_endpoint=True)
    if public_endpoint:
        private_endpoint = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_endpoint=True)
        public_url = urlparse(private_endpoint)
        private_url = urlparse(public_endpoint)
        public_loc = f'{public_url.scheme}://{public_url.netloc}'  # e.g.: https://some-host:8083
        private_loc = f'{private_url.scheme}://{private_url.netloc}'  # e.g.: http://localhost:8080
        log.info(public_loc)
        log.info(private_loc)
        datasets = [(ds_name, ds_url.replace(private_loc, public_loc)) for ds_name, ds_url in datasets]
        log.info(datasets)

    # Get initial option for dataset selector
    initial_dataset_option = datasets[0]
    log.debug(datasets)
    log.debug(initial_dataset_option)

    dataset_select = SelectInput(
        display_text='Dataset',
        name='dataset',
        multiple=False,
        options=datasets,
        initial=initial_dataset_option,
        select2_options={
            'placeholder': 'Select a dataset',
            'allowClear': False
        }
    )

    variable_select = SelectInput(
        display_text='Variable',
        name='variable',
        multiple=False,
        options=(),
        select2_options={
            'placeholder': 'Select a variable',
            'allowClear': False
        }
    )

    style_select = SelectInput(
        display_text='Style',
        name='style',
        multiple=False,
        options=(),
        select2_options={
            'placeholder': 'Select a style',
            'allowClear': False
        }
    )

    context = {
        'dataset_select': dataset_select,
        'variable_select': variable_select,
        'style_select': style_select,
    }
    return render(request, 'thredds_tutorial/home.html', context)


@controller
def get_wms_layers(request):
    json_response = {'success': False}

    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        wms_url = request.GET.get('wms_url', None)

        log.info(f'Retrieving layers for: {wms_url}')
        layers = get_layers_for_wms(wms_url)

        json_response.update({
            'success': True,
            'layers': layers
        })

    except Exception:
        json_response['error'] = f'An unexpected error has occurred. Please try again.'

    return JsonResponse(json_response)


@controller
def get_time_series_plot(request):
    context = {'success': False}

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        log.debug(f'POST: {request.POST}')

        geojson_str = str(request.POST.get('geometry', None))
        dataset = request.POST.get('dataset', None)
        variable = request.POST.get('variable', None)
        start_time = request.POST.get('start_time', None)
        end_time = request.POST.get('end_time', None)
        vertical_level = request.POST.get('vertical_level', None)

        # Deserialize GeoJSON string into Python objects
        try:
            geometry = geojson.loads(geojson_str)
        except JSONDecodeError:
            raise ValueError('Please draw an area of interest.')

        # Convert milliseconds from epoch to date time
        if start_time is not None:
            s = int(start_time) / 1000.0
            start_time = datetime.fromtimestamp(s)

        if end_time is not None:
            e = int(end_time) / 1000.0
            end_time = datetime.fromtimestamp(e)

        # Retrieve the connection to the THREDDS server
        catalog = app.get_spatial_dataset_service(app.THREDDS_SERVICE_NAME, as_engine=True)

        time_series = extract_time_series_at_location(
            catalog=catalog,
            geometry=geometry,
            dataset=dataset,
            variable=variable,
            start_time=start_time,
            end_time=end_time,
            vertical_level=vertical_level
        )

        log.debug(f'Time Series: {time_series}')

        figure = generate_figure(
            time_series=time_series,
            dataset=dataset,
            variable=variable
        )

        plot_view = PlotlyView(figure, height='200px', width='100%')

        context.update({
            'success': True,
            'plot_view': plot_view
        })

    except ValueError as e:
        context['error'] = str(e)

    except Exception:
        context['error'] = f'An unexpected error has occurred. Please try again.'
        log.exception('An unexpected error occurred.')

    return render(request, 'thredds_tutorial/plot.html', context)
