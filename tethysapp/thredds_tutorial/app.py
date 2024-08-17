from tethys_sdk.base import TethysAppBase


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
