"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config

from ..models import DBSession
from ..models import FarmComponent


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

    if request.current_route_url().startswith(request.route_url('configuration_views_home')):
        # configuration sidebar
        config_items.append(config_item('Field Settings', request.route_url('field_settings_list')))
        config_items.append(config_item('Farm Components', request.route_url('components_list')))
        config_items.append(config_item('Periphery Controllers', request.route_url('periphery_controllers_list')))
    if request.current_route_url().startswith(request.route_url('display_views_home')):
        # display sidebar
        components = DBSession.query(FarmComponent).all()

    return {'configuration_items': config_items,
            'components': components}
