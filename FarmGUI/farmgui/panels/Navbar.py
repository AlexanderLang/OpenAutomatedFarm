"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config


@panel_config(name='navbar', renderer='farmgui:panels/templates/navbar.pt')
def navbar(context, request):
    def nav_item(name, url):
        """

        :rtype : dict
        """
        active = request.current_route_url().startswith(url)
        item = {'name': name,
                'url': url,
                'active': active}
        return item

    nav_items = [
        nav_item('Hardware', request.route_url('hardware_views_home')),
        nav_item('Components', request.route_url('component_views_home')),
        nav_item('Settings', request.route_url('setting_views_home')),
        nav_item('Display', request.route_url('display_views_home')),
        nav_item('About', request.route_url('project_views_about')),
    ]
    return {'nav_items': nav_items}
