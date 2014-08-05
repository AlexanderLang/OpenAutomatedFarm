from time import mktime
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models import ParameterLog


class DisplayViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='display_views_home', renderer='templates/display_views_home.pt', layout='default')
    def display_views_home(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/plot_parameter.js'))
        layout.add_css(self.request.static_url('farmgui:static/css/plot_parameter.css'))
        return {"page_title": "Display"}

    @view_config(route_name='plot_parameter_data', renderer='json')
    def plot_parameter_data(self):
        logs = DBSession.query(ParameterLog).filter_by(parameter_id=1).all()
        data = []
        # axis limits
        time_offset = int(mktime(logs[0].time.date().timetuple()))
        xmin = int((mktime(logs[0].time.timetuple()) - time_offset) * 1000)
        for log in logs:
            millis = int((mktime(log.time.timetuple()) - time_offset) * 1000)
            data.append([millis, log.value])
        xmax = millis
        return {'xmin': xmin,
                'xmax': xmax,
                'data': [data]
                }