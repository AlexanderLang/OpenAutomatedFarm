'''
Created on Feb 25, 2014

@author: alex
'''

from pyramid_layout.panel import panel_config


@panel_config(name='navbar', renderer='farmgui:panels/templates/navbar.pt')
def Navbar(context, request):
    def nav_item(name, url):
        active = request.current_route_url().startswith(url)
        item = dict(
            name=name,
            url=url,
            active=active
            )
        return item
    nav_items = [
        nav_item('Plant Database', request.route_url('plant_settings_list')),
        nav_item('Field Controller', request.route_url('field_settings_list')),
        nav_item('About', request.route_url('about_view')),
        ]
    return {'nav_items': nav_items}
        