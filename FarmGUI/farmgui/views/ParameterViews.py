
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from plant_settings_database import DBSession as PlantSettings_Session
from plant_settings_database import Parameter

from ..schemas import ParameterSchema

class ParameterViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='parameters_list', renderer='farmgui:views/templates/parameters_list.pt', layout='default')
    def parameters_list(self):
        try:
            parameters = PlantSettings_Session.query(Parameter).all()
        except DBAPIError:
            return Response('database error (query Parameters)', content_type='text/plain', status_int=500)
        return {'parameters': parameters}
    
    @view_config(route_name='parameters_new', renderer='farmgui:views/templates/parameters_new.pt', layout='default')
    def parameters_new(self):
        response_dict = dict()
        addForm = Form(ParameterSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = addForm.validate(controls)
                new_parameter = Parameter(values['Name'], values['Unit'], values['Minimum'], values['Maximum'], values['Description'])
                PlantSettings_Session.add(new_parameter)
                return HTTPFound(location=self.request.route_url('parameters_list'))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}
        
