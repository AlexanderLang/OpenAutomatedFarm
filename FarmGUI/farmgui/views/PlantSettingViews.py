
from pyramid.view import view_config
from pyramid.response import Response
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
        response_dict = dict()
        addForm = Form(PlantSettingsSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        response_dict['addForm'] = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = addForm.validate(controls)
                new_setting = PlantSetting(values['Plant'], values['Variety'], values['Method'], values['Description'])
                PlantSettings_Session.add(new_setting)
            except ValidationFailure as e:
                response_dict['addForm'] = e.render()
        try:
            plant_settings = PlantSettings_Session.query(PlantSetting).all()
        except DBAPIError:
            return Response('database error.', content_type='text/plain', status_int=500)
        response_dict['plant_settings'] = plant_settings
        return response_dict
