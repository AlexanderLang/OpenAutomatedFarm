from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from farmgui.models import DBSession
from farmgui.models import PeripheryController

from farmgui.schemas import PeripheryControllerSchema


class HardwareViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='hardware_views_home',
                 renderer='farmgui:views/templates/periphery_controllers_list.pt',
                 layout='default')
    def periphery_controllers_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/hardware_functions.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/redis_values.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            periphery_controllers = DBSession.query(PeripheryController).all()
        except DBAPIError:
            return Response('database error (query PeripheryControllers)', content_type='text/plain', status_int=500)
        return {'periphery_controllers': periphery_controllers}

    @view_config(route_name='periphery_controller_update', renderer='json')
    def periphery_controller_update(self):
        ret_dict = {}
        controls = self.request.POST.items()
        pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['pc_id']).one()
        form = Form(PeripheryControllerSchema().bind(),
                    formid='edit_periphery_controller_form_' + str(pc.id),
                    action=self.request.route_url('periphery_controller_update', pc_id=pc.id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_periphery_controller(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['periphery_controller'] = pc.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        pc.name = vals['name']
        ret_dict['form'] = form.render(periphery_controller=pc)
        ret_dict['periphery_controller'] = pc.serialize
        self.request.redis.publish('periphery_controller_changes', 'changed '+str(pc.id))
        return ret_dict

    @view_config(route_name='periphery_controller_delete', renderer='json')
    def periphery_controller_delete(self):
        pc_id = self.request.matchdict['pc_id']
        pc = DBSession.query(PeripheryController).filter_by(_id=pc_id).one()
        DBSession.delete(pc)
        self.request.redis.publish('periphery_controller_changes', 'deleted '+str(pc_id))
        return {'delete': True}
