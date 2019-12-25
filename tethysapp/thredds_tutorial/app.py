from tethys_sdk.base import TethysAppBase, url_map_maker


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
        )

        return url_maps