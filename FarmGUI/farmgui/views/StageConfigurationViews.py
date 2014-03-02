
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from plant_settings_database import DBSession as PlantSettings_Session
from plant_settings_database import Stage
from plant_settings_database import Parameter
from plant_settings_database import StageConfiguration

from ..schemas import StageConfigurationSchema

class StageViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='stage_configuration_new', renderer='farmgui:views/templates/stage_configuration_new.pt', layout='default')
    def stage_configuration_new(self):
        response_dict = dict()
        addForm = Form(StageConfigurationSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                stage = PlantSettings_Session.query(Stage).filter(Stage._id==self.request.matchdict['_id']).first()
            except DBAPIError:
                return Response('database error.', content_type='text/plain', status_int=500)
            try:
                vals = addForm.validate(controls)
                param = PlantSettings_Session.query(Parameter).filter(Parameter._id==vals['parameter']).first()
                nsc = StageConfiguration(stage, param, vals['time'], vals['setpoint'], vals['upper_limit'], vals['lower_limit'])
                PlantSettings_Session.add(nsc)
                return HTTPFound(location=self.request.route_url('stage_view', _id=stage._id))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}
    