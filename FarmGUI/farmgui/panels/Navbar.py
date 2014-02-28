'''
Created on Feb 25, 2014

@author: alex
'''

from pyramid_layout.panel import panel_config


@panel_config(name='navbar', renderer='farmgui:panels/templates/navbar.pt')
def Navbar(context, request):
    def nav_item(name, url):
        active = request.current_route_url() == url
        item = dict(
            name=name,
            url=url,
            active=active
            )
        return item
    nav_items = [
        nav_item('Home', request.route_url('home_view')),
        nav_item('About', request.route_url('about_view')),
        ]
    return {'nav_items': nav_items}
        