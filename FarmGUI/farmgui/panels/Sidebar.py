"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config

from farmgui.models import DBSession
from farmgui.models import Parameter


@panel_config(name='sidebar', renderer='farmgui:panels/templates/sidebar.pt')
def sidebar(context, request):
    def config_item(name, url):
        active = request.current_route_url() == url
        item = dict(
            name=name,
            url=url,
            active=active
        )
        return item

    config_items = []
    components = []
    # display sidebar
    #if request.current_route_url().startswith(request.route_url('display_views_home')):
    #    components = DBSession.query(Parameter).all()

    return {'configuration_items': config_items,
            'components': components}
