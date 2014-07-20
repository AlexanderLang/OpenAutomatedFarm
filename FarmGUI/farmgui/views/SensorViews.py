
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models.field_controller import DBSession as Field_Controller_Session
from ..models.field_controller import Sensor

from ..schemas import ParameterSchema

class SensorViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='sensor_view', renderer='farmgui:views/templates/sensor_view.pt', layout='default')
    def sensor_view(self):
        try:
            sensor = Field_Controller_Session.query(Sensor).filter(Sensor._id==self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query Sensors for id)', content_type='text/plain', status_int=500)
        return {'sensor': sensor}
        
