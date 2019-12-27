from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import SpatialDatasetServiceSetting


class ThreddsTutorial(TethysAppBase):
    """
    Tethys app class for Thredds Tutorial.
    """

    name = 'THREDDS Tutorial'
    index = 'thredds_tutorial:home'
    icon = 'thredds_tutorial/images/unidata_logo.png'
    package = 'thredds_tutorial'
    root_url = 'thredds-tutorial'
    color = '#008e8d'

    THREDDS_SERVICE_NAME = 'thredds_service'

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='thredds-tutorial',
                controller='thredds_tutorial.controllers.home'
            ),
            UrlMap(
                name='get_wms_layers',
                url='thredds-tutorial/get-wms-layers',
                controller='thredds_tutorial.controllers.get_wms_layers'
            ),
            UrlMap(
                name='get_time_series_plot',
                url='thredds-tutorial/get-time-series-plot',
                controller='thredds_tutorial.controllers.get_time_series_plot'
            ),
        )

        return url_maps

    def spatial_dataset_service_settings(self):
        """
        Example spatial_dataset_service_settings method.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name=self.THREDDS_SERVICE_NAME,
                description='THREDDS service for app to use',
                engine=SpatialDatasetServiceSetting.THREDDS,
                required=True,
            ),
        )

        return sds_settings
