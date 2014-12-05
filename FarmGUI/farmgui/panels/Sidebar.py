"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config

from farmgui.models import DBSession
from farmgui.models import PeripheryController


@panel_config(name='sidebar', renderer='farmgui:panels/templates/sidebar.pt')
def sidebar(context, request):
    processes = []
    processes.append({'name': 'Farm Supervisor',
                       'cpu_key': 'fs-cpu',
                       'mem_key': 'fs-mem'})
    processes.append({'name': 'Farm Manager',
                       'cpu_key': 'fm-cpu',
                       'mem_key': 'fm-mem'})
    processes.append({'name': 'Pyramid',
                       'cpu_key': 'ps-cpu',
                       'mem_key': 'ps-mem'})
    processes.append({'name': 'MySQL',
                       'cpu_key': 'db-cpu',
                       'mem_key': 'db-mem'})
    processes.append({'name': 'Redis',
                       'cpu_key': 'redis-cpu',
                       'mem_key': 'redis-mem'})
    pcs = DBSession.query(PeripheryController).all()
    for pc in pcs:
        processes.append({'name': pc.name,
                          'cpu_key': 'pc-cpu-'+str(pc.id),
                          'mem_key': 'pc-mem-'+str(pc.id)})
    return {'processes': processes}

@panel_config(name='process_panel', renderer='farmgui:panels/templates/process_panel.pt')
def process_panel(context, request):
    return {'proc': context}
