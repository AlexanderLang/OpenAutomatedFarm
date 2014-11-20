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
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/display_periphery_controller_values.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            periphery_controllers = DBSession.query(PeripheryController).all()
        except DBAPIError:
            return Response('database error (query PeripheryControllers)', content_type='text/plain', status_int=500)
        return {'periphery_controllers': periphery_controllers}

    @view_config(route_name='periphery_controller_update')
    def periphery_controller_update(self):
        try:
            pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        form = Form(PeripheryControllerSchema(), buttons=('Save',))
        controls = self.request.POST.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        pc.name = values['name']
        return HTTPFound(location=self.request.route_url('periphery_controllers_list'))

    @view_config(route_name='periphery_controller_delete')
    def periphery_controller_delete(self):
        pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['_id']).first()
        DBSession.delete(pc)
        return HTTPFound(location=self.request.route_url('periphery_controllers_list'))
