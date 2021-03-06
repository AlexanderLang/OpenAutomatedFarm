"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config

from farmgui.models import DBSession
from farmgui.models import PeripheryController


@panel_config(name='sidebar', renderer='farmgui:panels/templates/sidebar.pt')
def sidebar(context, request):
    processes = [{'name': 'Total',
                  'cpu_key': 'total-cpu',
                  'mem_key': 'total-mem'},
                 {'name': 'Farm Supervisor',
                  'cpu_key': 'fs-cpu',
                  'mem_key': 'fs-mem'},
                 {'name': 'Farm Manager',
                  'cpu_key': 'fm-cpu',
                  'mem_key': 'fm-mem'},
                 {'name': 'Periphery Controller',
                  'cpu_key': 'pc-cpu',
                  'mem_key': 'pc-mem'},
                 {'name': 'Pyramid',
                  'cpu_key': 'ps-cpu',
                  'mem_key': 'ps-mem'},
                 {'name': 'MySQL',
                  'cpu_key': 'db-cpu',
                  'mem_key': 'db-mem'},
                 {'name': 'Redis',
                  'cpu_key': 'redis-cpu',
                  'mem_key': 'redis-mem'}]
    return {'processes': processes}


@panel_config(name='process_panel', renderer='farmgui:panels/templates/process_panel.pt')
def process_panel(context, request):
    return {'proc': context}
