"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config


@panel_config(name='sidebar', renderer='farmgui:panels/templates/sidebar.pt')
def sidebar(context, request):
    def sidebar_item(name, url):
        active = request.current_route_url() == url
        item = dict(
            name=name,
            url=url,
            active=active
        )
        return item

    sidebar_items = []

    if request.current_route_url().startswith(request.route_url('configuration_views_home')):
        # configuration sidebar
        sidebar_items.append(sidebar_item('Field Settings', request.route_url('field_settings_list')))
        sidebar_items.append(sidebar_item('Farm Components', request.route_url('components_list')))

    return {'sidebar_items': sidebar_items}
