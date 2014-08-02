from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models import PlantSetting

from ..schemas import PlantSettingsSchema


class PlantSettingViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='plant_settings_list', renderer='farmgui:views/templates/plant_settings_list.pt',
                 layout='default')
    def plant_settings_list(self):
        try:
            plant_settings = DBSession.query(PlantSetting).all()
        except DBAPIError:
            return Response('database error (query PlantSettings)', content_type='text/plain', status_int=500)
        return {'plant_settings': plant_settings}

    @view_config(route_name='plant_settings_new', renderer='farmgui:views/templates/plant_settings_new.pt',
                 layout='default')
    def plant_settings_new(self):
        add_form = Form(PlantSettingsSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = add_form.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                values = add_form.validate(controls)
                new_setting = PlantSetting(values['Plant'], values['Variety'], values['Method'], values['Description'])
                DBSession.add(new_setting)
                return HTTPFound(location=self.request.route_url('plant_settings_list'))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}

    @view_config(route_name='plant_settings_view', renderer='farmgui:views/templates/plant_settings_view.pt',
                 layout='default')
    def plant_settings_view(self):
        try:
            plant_setting = DBSession.query(PlantSetting).filter(
                PlantSetting.id == self.request.matchdict['_id']).first()
            return {'plant_setting': plant_setting}
        except DBAPIError:
            return Response('database error (query PlantSettings for id)', content_type='text/plain', status_int=500)
