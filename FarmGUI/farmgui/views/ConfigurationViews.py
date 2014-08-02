
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models import FarmComponent
from ..models import Parameter
from ..models import ParameterType
from ..models import Sensor
from ..models import FieldSetting

from ..schemas import FarmComponentSchema
from ..schemas import ParameterSchema

class ConfigurationViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='configuration_views_home')
    def configuration_views_home(self):
        return HTTPFound(location=self.request.route_url('components_list'))
    
    @view_config(route_name='field_settings_list', renderer='farmgui:views/templates/field_settings_list.pt', layout='default')
    def field_settings_list(self):
        try:
            field_settings = DBSession.query(FieldSetting).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}
    
    @view_config(route_name='components_list', renderer='farmgui:views/templates/components_list.pt', layout='default')
    def components_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        addForm = Form(FarmComponentSchema(), formid='addForm', buttons=('Save',))
        add_component_error = False
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = addForm.validate(controls)
                new_component = FarmComponent(values['Name'], values['Description'])
                DBSession.add(new_component)
            except ValidationFailure as e:
                addForm = e
                add_component_error = True
        try:
            components = DBSession.query(FarmComponent).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'components': components,
                'add_component_form': addForm.render(),
                'add_component_error': add_component_error
                }
    
    @view_config(route_name='component_delete')
    def component_delete(self):
        comp = DBSession.query(FarmComponent).filter(FarmComponent._id == self.request.matchdict['_id']).first()
        DBSession.delete(comp)
        return HTTPFound(location=self.request.route_url('configuration_views_home'))
    
    @view_config(route_name='parameter_save', renderer='farmgui:views/templates/parameter_save.pt', layout='default')
    def parameter_save(self):
        controls = self.request.POST
        addForm = Form(ParameterSchema().bind())
        print('\n\nSaving parameter...\n'+str(controls))
        try:
            p = addForm.validate(controls.items())
            print('\n\nparameter form:\n\n'+str(p))
            comp = DBSession.query(FarmComponent).filter(FarmComponent._id == p['component']).first()
            parameter_type = DBSession.query(ParameterType).filter(ParameterType._id == p['parameter_type']).first()
            sensor = DBSession.query(Sensor).filter(Sensor._id == p['sensor']).first()
            new_par = Parameter(comp, p['name'], parameter_type, p['interval'], sensor, p['description'])
            DBSession.add(new_par)
        except ValidationFailure as e:
            addForm = e
            return {'addForm': addForm.render()}
        return HTTPFound(location=self.request.route_url('configuration_views_home'))
    
    @view_config(route_name='parameter_delete')
    def parameter_delete(self):
        parameter = DBSession.query(Parameter).filter(Parameter._id == self.request.matchdict['_id']).first()
        DBSession.delete(parameter)
        return HTTPFound(location=self.request.route_url('configuration_views_home'))
