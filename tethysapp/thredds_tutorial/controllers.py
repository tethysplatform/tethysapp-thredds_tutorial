from django.shortcuts import render
from tethys_sdk.routing import controller
from tethys_sdk.gizmos import SelectInput, PlotlyView
from .app import App
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from .thredds_methods import parse_datasets, get_layers_for_wms, extract_time_series_at_location
from .figure import generate_figure
import requests
import logging
import geojson
from datetime import datetime
from simplejson.errors import JSONDecodeError

log = logging.getLogger(__name__)

@controller
def home(request):
    """
    Controller for the app home page.
    """
    catalog = App.get_spatial_dataset_service(App.THREDDS_SERVICE_NAME, as_engine=True)

    # Retrieve dataset options from the THREDDS service
    log.info('Retrieving Datasets...')
    datasets = parse_datasets(catalog)
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
    return App.render(request, 'home.html', context)

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

@controller(name='getWMSImageFromServer', url='getWMSImageFromServer/')
def wms_image_from_server(request):
    try:
        if 'main_url' in request.GET:
            request_url = request.GET.get('main_url')
            query_params = request.GET.dict()
            query_params.pop('main_url', None)
            r = requests.get(request_url, params=query_params)
            return HttpResponse(r.content, content_type="image/png")
        else:
            return JsonResponse({})
    except Exception as e:
        log.info(e)
        return JsonResponse({'error': e})
    
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
        catalog = App.get_spatial_dataset_service(App.THREDDS_SERVICE_NAME, as_engine=True)

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

    return App.render(request, 'plot.html', context)