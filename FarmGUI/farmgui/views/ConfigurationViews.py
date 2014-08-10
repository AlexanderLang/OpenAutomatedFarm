from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from json import dump

from ..models import DBSession
from ..models import serialize
from ..models import FarmComponent
from ..models import Parameter
from ..models import ParameterType
from ..models import Sensor
from ..models import FieldSetting
from ..models import PeripheryController
from ..models import Device
from ..models import DeviceType
from ..models import Actuator

from ..schemas import FarmComponentSchema
from ..schemas import PeripheryControllerSchema
from ..schemas import ParameterSchema
from ..schemas import FieldSettingSchema
from ..schemas import DeviceSchema


class ConfigurationViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='configuration_views_home')
    def configuration_views_home(self):
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='field_settings_list', renderer='farmgui:views/templates/field_settings_list.pt',
                 layout='default')
    def field_settings_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            field_settings = DBSession.query(FieldSetting).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}

    @view_config(route_name='field_setting_update')
    def field_setting_update(self):
        try:
            fs = DBSession.query(FieldSetting).filter_by(name=self.request.matchdict['name']).first()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        form = Form(FieldSettingSchema(), buttons=('Save',))
        controls = self.request.POST
        controls['name'] = fs.name
        controls['description'] = fs.description
        controls = controls.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        fs.value = values['value']
        return HTTPFound(location=self.request.route_url('field_settings_list'))

    @view_config(route_name='components_list', renderer='farmgui:views/templates/components_list.pt', layout='default')
    def components_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        add_form = Form(FarmComponentSchema(),
                        formid='addForm',
                        action=self.request.route_url('component_save', _id=0),
                        buttons=('Save',))
        try:
            components = DBSession.query(FarmComponent).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'components': components,
                'add_component_form': add_form.render()}

    @view_config(route_name='component_save')
    def component_save(self):
        if self.request.matchdict['_id'] == '0':
            # new component
            add_form = Form(FarmComponentSchema(),
                        formid='addForm',
                        action=self.request.route_url('component_save', _id=0),
                        buttons=('Save',))
            controls = self.request.POST.items()
            try:
                values = add_form.validate(controls)
            except ValidationFailure as e:
                return Response(e.render())
            new_component = FarmComponent(values['Name'], values['Description'])
            DBSession.add(new_component)
            DBSession.flush()
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='component_delete')
    def component_delete(self):
        comp = DBSession.query(FarmComponent).filter_by(_id=self.request.matchdict['_id']).first()
        DBSession.delete(comp)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='parameter_save', renderer='farmgui:views/templates/parameter_save.pt', layout='default')
    def parameter_save(self):
        controls = self.request.POST
        add_form = Form(ParameterSchema().bind())
        try:
            p = add_form.validate(controls.items())
            comp = DBSession.query(FarmComponent).filter_by(_id=p['component']).first()
            parameter_type = DBSession.query(ParameterType).filter_by(_id=p['parameter_type']).first()
            sensor = DBSession.query(Sensor).filter_by(_id=p['sensor']).first()
            new_par = Parameter(comp, p['name'], parameter_type, p['interval'], sensor, p['description'])
            DBSession.add(new_par)
        except ValidationFailure as e:
            add_form = e
            return {'addForm': add_form.render()}
        self.request.redis.publish('parameter_changes', 'new parameter')
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='parameter_delete')
    def parameter_delete(self):
        parameter = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['_id']).first()
        DBSession.delete(parameter)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='parameter_update')
    def parameter_update(self):
        try:
            p = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query Parameters)', content_type='text/plain', status_int=500)
        form = Form(ParameterSchema().bind(parameter=p), buttons=('Save',))
        controls = self.request.POST
        controls['component'] = p.component_id
        if controls['sensor'] == 'None':
            controls['sensor'] = None
        controls = controls.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        p.name = values['name']
        p.parameter_type_id = values['parameter_type']
        p.interval = values['interval']
        if values['sensor'] is not None:
            p.sensor_id = values['sensor']
        p.description = values['description']
        self.request.redis.publish('parameter_changes', 'parameter changed')
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='device_save', renderer='farmgui:views/templates/device_save.pt', layout='default')
    def device_save(self):
        controls = self.request.POST
        add_form = Form(DeviceSchema().bind(), buttons=('Save',))
        try:
            d = add_form.validate(controls.items())
            comp = DBSession.query(FarmComponent).filter_by(_id=d['component']).first()
            device_type = DBSession.query(DeviceType).filter_by(_id=d['device_type']).first()
            actuator = DBSession.query(Actuator).filter_by(_id=d['actuator']).first()
            new_dev = Device(comp, d['name'], device_type, actuator, d['description'])
            DBSession.add(new_dev)
        except ValidationFailure as e:
            add_form = e
            return {'addForm': add_form.render()}
        self.request.redis.publish('device_changes', 'new device')
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='device_delete')
    def device_delete(self):
        device = DBSession.query(Device).filter_by(_id=self.request.matchdict['_id']).first()
        DBSession.delete(device)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='device_update')
    def device_update(self):
        try:
            d = DBSession.query(Device).filter_by(_id=self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query Devices)', content_type='text/plain', status_int=500)
        form = Form(DeviceSchema().bind(device=d), buttons=('Save',))
        controls = self.request.POST
        controls['component'] = d.component_id
        if controls['actuator'] == 'None':
            controls['actuator'] = None
        controls = controls.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        d.name = values['name']
        d.device_type_id = values['device_type']
        if values['actuator'] is not None:
            d.actuator_id = values['actuator']
        d.description = values['description']
        self.request.redis.publish('device_changes', 'device changed')
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='periphery_controllers_list',
                 renderer='farmgui:views/templates/periphery_controllers_list.pt', layout='default')
    def periphery_controllers_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            periphery_controllers = DBSession.query(PeripheryController).all()
        except DBAPIError:
            return Response('database error (query PeripheryControllers)', content_type='text/plain', status_int=500)
        return {'periphery_controllers': periphery_controllers}

    @view_config(route_name='periphery_controller_update')
    def periphery_controller_update(self):
        try:
            pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        form = Form(PeripheryControllerSchema(), buttons=('Save',))
        controls = self.request.POST.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        pc.name = values['name']
        return HTTPFound(location=self.request.route_url('periphery_controllers_list'))
