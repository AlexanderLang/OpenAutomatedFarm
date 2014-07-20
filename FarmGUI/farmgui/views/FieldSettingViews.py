
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models.field_controller import DBSession as Field_Controller_Session
from ..models.field_controller import FieldSetting

from ..schemas import PlantSettingsSchema

import transaction

class FieldSettingViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='field_settings_list', renderer='farmgui:views/templates/field_settings_list.pt', layout='default')
    def field_settings_list(self):
        try:
            field_settings = Field_Controller_Session.query(FieldSetting).all()
            if 'save' in self.request.POST:
                for fs in field_settings:
                    fs.value = self.request.POST.get(fs.name)
                #transaction.commit()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}
