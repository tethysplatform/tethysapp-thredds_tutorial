from owslib.wms import WebMapService
import requests
import chardet
import logging
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

def parse_datasets(catalog):
    """
    Collect all available datasets that have the WMS service enabled.

    Args:
        catalog(siphon.catalog.TDSCatalog): A Siphon catalog object bound to a valid THREDDS service.

    Returns:
        list<2-tuple<dataset_name, wms_url>: One 2-tuple for each dataset.
    """
    datasets = []   
    
    for dataset_name, dataset_obj in catalog.datasets.items():
        dataset_wms_url = dataset_obj.access_urls.get('wms', None)
        if dataset_wms_url:
            datasets.append((dataset_name, f'{dataset_name};{dataset_wms_url}'))

    for _, catalog_obj in catalog.catalog_refs.items():
        d = parse_datasets(catalog_obj.follow())
        datasets.extend(d)
    
    return datasets

def get_layers_for_wms(wms_url):
    """
    Retrieve metadata from a WMS service including layers, available styles, and the bounding box.

    Args:
        wms_url(str): URL to the WMS service endpoint.

    Returns:
        dict<layer_name:dict<styles,bbox>>: A dictionary with a key for each WMS layer available and a dictionary value containing metadata about the layer.
    """
    params = {
        'service': 'WMS',
        'version': '1.1.1',
        'request': 'GetCapabilities'
    }
    request_url = f"{wms_url}?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    
    response = requests.get(request_url)
    encoding = chardet.detect(response.content)['encoding']
    
    response_content = response.content.decode(encoding)
    utf8_content = response_content.encode('utf-8')
            
    wms = WebMapService(None, xml=utf8_content)

    layers = wms.contents
    log.debug('WMS Contents:')
    log.debug(layers)

    layers_dict = dict()
    for layer_name, layer in layers.items():
        layer_styles = layer.styles
        layer_bbox = layer.boundingBoxWGS84
        leaflet_bbox = [[layer_bbox[1], layer_bbox[0]], [layer_bbox[3], layer_bbox[2]]]
        layers_dict.update({
            layer_name: {
                'styles': layer_styles,
                'bbox': leaflet_bbox
            }
        })

    log.debug('Layers Dict:')
    log.debug(layers_dict)
    return layers_dict

def find_dataset(catalog, dataset):
    """
    Recursively search a TDSCatalog for a dataset with the given name.

    Args:
        catalog(siphon.catalog.TDSCatalog): A Siphon catalog object bound to a valid THREDDS service.
        dataset(str): The name of the dataset to find.

    Returns:
        siphon.catalog.Dataset: The catalog dataset object or None if not found.
    """
    if dataset in catalog.datasets:
        return catalog.datasets[dataset]

    for catalog_name, catalog_obj in catalog.catalog_refs.items():
        d = find_dataset(catalog_obj.follow(), dataset)
        if d is not None:
            return d

    return None

def extract_time_series_at_location(catalog, geometry, dataset, variable, start_time=None, end_time=None,
                                    vertical_level=None):
    """
    Extract a time series from a THREDDS dataset at the given location.

    Args:
        catalog(siphon.catalog.TDSCatalog): a Siphon catalog object bound to a valid THREDDS service.
        geometry(geojson): A geojson object representing the location.
        dataset(str): Name of the dataset to query.
        variable(str): Name of the variable to query.
        start_time(datetime): Start of time range to query. Defaults to datetime.utcnow().
        end_time(datetime): End of time range to query. Defaults to 7 days after start_time.
        vertical_level(number): The vertical level to query. Defaults to 100000.

    Returns:
        netCDF5.Dataset: The data from the NCSS query.
    """
    try:
        d = find_dataset(catalog, dataset)
        ncss = d.subset()
        query = ncss.query()

        # Filter by location
        coordinates = geometry.geometry.coordinates
        query.lonlat_point(coordinates[0], coordinates[1])

        # Filter by time
        if start_time is None:
            start_time = datetime.utcnow()

        if end_time is None:
            end_time = start_time + timedelta(days=7)

        query.time_range(start_time, end_time)

        # Filter by variable
        query.variables(variable).accept('netcdf')

        # Filter by vertical level
        if vertical_level is not None:
            query.vertical_level(vertical_level)
        else:
            query.vertical_level(100000)

        # Get the data
        data = ncss.get_data(query)

    except OSError as e:
        if 'NetCDF: Unknown file format' in str(e):
            raise ValueError("We're sorry, but we don't support querying this type of dataset at this time. "
                             "Please try another dataset.")
        else:
            raise e

    return data