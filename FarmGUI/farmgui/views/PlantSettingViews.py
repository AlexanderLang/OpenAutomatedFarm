
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from plant_settings_database import DBSession as PlantSettings_Session
from plant_settings_database import PlantSetting

from ..schemas import PlantSettingsSchema

class PlantSettingViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='plant_settings_view', renderer='farmgui:views/templates/plant_settings.pt', layout='default')
    def plant_settings_view(self):
        try:
            plant_settings = PlantSettings_Session.query(PlantSetting).all()
        except DBAPIError:
            return Response('database error.', content_type='text/plain', status_int=500)
        return {'plant_settings': plant_settings}
    
    @view_config(route_name='add_plant_settings_view', renderer='farmgui:views/templates/add_plant_settings.pt', layout='default')
    def add_plant_settings_view(self):
        response_dict = dict()
        addForm = Form(PlantSettingsSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = addForm.validate(controls)
                new_setting = PlantSetting(values['Plant'], values['Variety'], values['Method'], values['Description'])
                PlantSettings_Session.add(new_setting)
                return HTTPFound(location=self.request.route_url('plant_settings_view'))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}
        
