from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from farmgui.models import DBSession
from farmgui.models import serialize
from farmgui.models import FieldSetting

from farmgui.schemas import FieldSettingSchema


class SettingViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='setting_views_home',
                 renderer='farmgui:views/templates/setting_views_home.pt',
                 layout='default')
    def setting_views_home(self):
        """
        display a list of all field settings

        """
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            field_settings = DBSession.query(FieldSetting).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}

    @view_config(route_name='setting_views_update', renderer='json')
    def setting_views_update(self):
        ret_dict = {}
        controls = self.request.POST
        try:
            fs = DBSession.query(FieldSetting).filter_by(name=self.request.matchdict['name']).first()
        except DBAPIError:
            ret_dict['error'] = True
            return ret_dict
        form = Form(FieldSettingSchema(), buttons=('Save',))
        controls['name'] = fs.name
        controls['description'] = fs.description
        controls = controls.items()
        try:
            values = form.validate(controls)
            fs.value = values['value']
            ret_dict['form'] = form.render(field_setting=fs)
            ret_dict['component'] = serialize(fs)
            self.request.redis.publish('field_setting_changes', 'parameter changed')
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
        return ret_dict
