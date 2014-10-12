import time
from time import mktime
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ..models import DBSession
from ..models import PeripheryController
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
        for i in self.request.POST.items():
            if i[0] == 'parameter_ids':
                p_ids.append(i[1])
            if i[0] == 'plot_period':
                period = int(i[1])
        now = datetime.now()
        start_time = now - timedelta(seconds=period/1000)
        utc_offset = time.altzone * 1000
        now_millis = int(mktime(now.timetuple())*1000) - utc_offset
        start_time_millis = now_millis - period
        data = []
        for pid in p_ids:
            logs = DBSession.query(ParameterLog).filter_by(parameter_id=pid).filter(ParameterLog.time >= start_time).order_by(asc(ParameterLog.time)).all()
            series = []
            for log in logs:
                millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                series.append([millis, log.value])
            data.append(series)
        return {'xmin': start_time_millis,
                'xmax': now_millis,
                'data': data
                }

    @view_config(route_name='periphery_controller_values', renderer='json')
    def periphery_controller_values(self):
        pc_id = self.request.matchdict['pc_id']
        values = {}
        for sensor_key in eval(self.request.redis.get('pc' + pc_id + '.s')):
            values[sensor_key] = self.request.redis.get(sensor_key).decode('utf-8')
        for actuator_key in eval(self.request.redis.get('pc' + pc_id + '.a')):
            raw = self.request.redis.get(actuator_key)
            if raw is None:
                raw = self.request.redis.get(actuator_key + '.default')
            values[actuator_key] = raw.decode('utf-8')
        return values