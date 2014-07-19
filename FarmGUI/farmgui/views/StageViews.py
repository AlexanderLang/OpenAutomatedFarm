
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from plant_settings_database import DBSession as PlantSettings_Session
from plant_settings_database import PlantSetting
from plant_settings_database import Stage

from ..schemas import StageSchema

class StageViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='stage_new', renderer='farmgui:views/templates/stage_new.pt', layout='default')
    def stage_new(self):
        response_dict = dict()
        addForm = Form(StageSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = addForm.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                plant_setting = PlantSettings_Session.query(PlantSetting).filter(PlantSetting._id==self.request.matchdict['_id']).first()
            except DBAPIError:
                return Response('database error (query PlantSettings for id)', content_type='text/plain', status_int=500)
            try:
                values = addForm.validate(controls)
                new_stage = Stage(plant_setting, values['Number'], values['Duration'], values['Name'], values['Description'])
                PlantSettings_Session.add(new_stage)
                return HTTPFound(location=self.request.route_url('plant_settings_view', _id=plant_setting._id))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}
    
    @view_config(route_name='stage_view', renderer='farmgui:views/templates/stage_view.pt', layout='default')
    def stage_view(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/plot_configuration.js'))
        layout.add_css(self.request.static_url('farmgui:static/css/plot_configuration.css'))
        try:
            stage = PlantSettings_Session.query(Stage).filter(Stage._id==self.request.matchdict['_id']).first()
            return {'stage': stage}
        except DBAPIError:
            return Response('database error (query Stages for id)', content_type='text/plain', status_int=500)
    