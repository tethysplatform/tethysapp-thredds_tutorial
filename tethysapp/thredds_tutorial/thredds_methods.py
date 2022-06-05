from owslib.wms import WebMapService
import logging

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
    wms = WebMapService(wms_url)
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
