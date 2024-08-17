from tethys_sdk.base import TethysAppBase


class App(TethysAppBase):
    """
    Tethys app class for Thredds Tutorial.
    """

    name = 'Thredds Tutorial'
    description = ''
    package = 'thredds_tutorial'  # WARNING: Do not change this value
    index = 'home'
    icon = f'{package}/images/icon.gif'
    root_url = 'thredds-tutorial'
    color = '#c23616'
    tags = ''
    enable_feedback = False
    feedback_emails = []