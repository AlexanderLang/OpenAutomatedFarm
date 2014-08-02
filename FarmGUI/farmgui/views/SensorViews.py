from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models import Sensor


class SensorViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='sensor_view', renderer='farmgui:views/templates/sensor_view.pt', layout='default')
    def sensor_view(self):
        try:
            sensor = DBSession.query(Sensor).filter(Sensor.id == self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query Sensors for id)', content_type='text/plain', status_int=500)
        return {'sensor': sensor}
