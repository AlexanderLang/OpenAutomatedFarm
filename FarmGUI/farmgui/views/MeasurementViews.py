
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError
from sqlalchemy import cast
from sqlalchemy import asc
from sqlalchemy import Time

from ..models import DBSession
from ..models import FarmComponent
from ..models import Parameter
from ..models import Sensor
from ..models import MeasurementLog

from ..schemas import MeasurementSchema

from time import mktime
from datetime import date
from datetime import datetime
from datetime import timedelta

class MeasurementViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='measurements_list', renderer='farmgui:views/templates/measurements_list.pt', layout='default')
    def measurements_list(self):
        try:
            measurements = DBSession.query(Measurement).all()
        except DBAPIError:
            return Response('database error (query Measurements)', content_type='text/plain', status_int=500)
        return {'measurements': measurements}
    
    @view_config(route_name='measurements_new', renderer='farmgui:views/templates/measurements_new.pt', layout='default')
    def measurement_new(self):
        addForm = Form(MeasurementSchema().bind(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = addForm.validate(controls)
                location = DBSession.query(FarmComponent).filter(FarmComponent._id==values['location']).first()
                parameter = DBSession.query(Parameter).filter(Parameter._id==values['parameter']).first()
                sensor = DBSession.query(Sensor).filter(Sensor._id==values['sensor']).first()
                DBSession.add(Measurement(location, parameter, sensor, values['interval'], values['description']))
                self.request.redis.publish('measurement_changes', 'some data')
                return HTTPFound(location=self.request.route_url('measurements_list'))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}
    
    @view_config(route_name='measurement_view', renderer='farmgui:views/templates/measurement_view.pt', layout='default')
    def measurement_view(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/plot_measurement_log.js'))
        layout.add_css(self.request.static_url('farmgui:static/css/plot_configuration.css'))
        
        try:
            m = DBSession.query(Measurement).filter(Measurement._id==self.request.matchdict['measurement_id']).first()
        except DBAPIError:
            return Response('database error (query Measurements for id)', content_type='text/plain', status_int=500)
        if 'save' in self.request.POST:
            form = Form(MeasurementSchema().bind(), formid='form', buttons=('Save',), use_ajax=True)
            controls = self.request.POST
            controls['location'] = m.location._id
            controls['parameter'] = m.parameter._id
            controls = controls.items()
            try:
                values = form.validate(controls)
                m.sensor = DBSession.query(Sensor).filter(Sensor._id==values['sensor']).first()
                m.interval = values['interval']
                m.description = values['description']
                self.request.redis.publish('measurement_changes', '')
            except ValidationFailure as e:
                form = e.render()
                return {'measurement': m,
                    'form': form,
                    'error': True}
        form = Form(MeasurementSchema().bind(measurement=m), formid='form', buttons=('Save',), use_ajax=True)
        return {'measurement': m,
                    'form': form,
                    'error': False}
        
    @view_config(route_name='measurement_log_json', renderer='json')
    def measurement_log_json(self):
        starttime = datetime.now() - timedelta(minutes=15)
        logs = DBSession.query(MeasurementLog).filter_by(measurementId=self.request.matchdict['measurement_id'])
        logs = logs.filter(MeasurementLog.time > starttime)
        logs = logs.order_by(asc(MeasurementLog.time)).all()
        data = []
        xmin = 0
        xmax = 10
        if len(logs) > 0:
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
