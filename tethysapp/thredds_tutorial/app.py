from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import SpatialDatasetServiceSetting

class App(TethysAppBase):
    """
    Tethys app class for Thredds Tutorial.
    """
    name = 'Thredds Tutorial'
    description = ''
    package = 'thredds_tutorial'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/unidata_logo.png'
    root_url = 'thredds-tutorial'
    color = '#008e8d'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    THREDDS_SERVICE_NAME = 'thredds_service'

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
