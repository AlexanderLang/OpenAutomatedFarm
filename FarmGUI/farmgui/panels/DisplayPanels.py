"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config


@panel_config(name='plot_parameter', renderer='farmgui:panels/templates/plot_parameter.pt')
def plot_parameter(context, request):
    """

    """
    return {}
