"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config

from farmgui.models import DBSession
from farmgui.models import Parameter


@panel_config(name='sidebar', renderer='farmgui:panels/templates/sidebar.pt')
def sidebar(context, request):
    return {}
