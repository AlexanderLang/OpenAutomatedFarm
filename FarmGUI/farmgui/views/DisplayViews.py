from time import mktime
from datetime import datetime
from datetime import timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models import ParameterLog
from sqlalchemy import asc


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
        period = 0
        p_ids = []
        print('Post: '+str(self.request.POST))
        for i in self.request.POST.items():
            if i[0] == 'parameter_ids':
                p_ids.append(i[1])
            if i[0] == 'plot_period':
                period = int(i[1])
        print('period: '+str(period))
        print('p_ids:  '+str(p_ids))
        start_time = datetime.now() - timedelta(seconds=period/1000)
        xmin = 0
        xmax = period
        data = []
        print('start_time: '+str(start_time))
        for pid in p_ids:
            logs = DBSession.query(ParameterLog).filter_by(parameter_id=pid).filter(ParameterLog.time >= start_time).order_by(asc(ParameterLog.time)).all()
            series = []
            for log in logs:
                millis = int((mktime(log.time.timetuple()) - mktime(start_time.timetuple())) * 1000)
                series.append([millis, log.value])
            data.append(series)
        return {'xmin': xmin,
                'xmax': xmax,
                'data': data
                }