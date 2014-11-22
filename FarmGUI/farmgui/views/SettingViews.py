from pyramid.view import view_config
from pyramid.response import Response
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from farmgui.models import DBSession
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
        layout.add_javascript(self.request.static_url('farmgui:static/js/setting_functions.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            field_settings = DBSession.query(FieldSetting).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}

    @view_config(route_name='field_setting_update', renderer='json')
    def setting_views_update(self):
        ret_dict = {}
        controls = self.request.POST.items()
        fs = DBSession.query(FieldSetting).filter_by(name=self.request.matchdict['name']).one()
        form = Form(FieldSettingSchema().bind(),
                    formid='edit_field_setting_form_' + fs.name,
                    action=self.request.route_url('field_setting_update', name=fs.name),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_field_setting(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['field_setting'] = fs.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        fs.value = vals['value']
        ret_dict['form'] = form.render(field_setting=fs)
        ret_dict['field_setting'] = fs.serialize
        self.request.redis.publish('field_setting_changes', str(fs.serialize))
        return ret_dict
