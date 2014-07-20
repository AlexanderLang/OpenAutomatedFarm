
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models.field_controller import DBSession as Field_Controller_Session
from ..models.field_controller import PeripheryController

class PeripheryControllerViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='periphery_controllers_list', renderer='farmgui:views/templates/periphery_controllers_list.pt', layout='default')
    def periphery_controllers_list(self):
        try:
            periphery_controllers = Field_Controller_Session.query(PeripheryController).all()
        except DBAPIError:
            return Response('database error (query PeripheryControllers)', content_type='text/plain', status_int=500)
        return {'periphery_controllers': periphery_controllers}
    
    @view_config(route_name='periphery_controller_view', renderer='farmgui:views/templates/periphery_controller_view.pt', layout='default')
    def periphery_controller_view(self):
        try:
            periphery_controller = Field_Controller_Session.query(PeripheryController).filter(PeripheryController._id==self.request.matchdict['_id']).first()
            if 'save' in self.request.POST:
                periphery_controller.name = self.request.POST.get('name')
        except DBAPIError:
            return Response('database error (query PeripheryControllers for id)', content_type='text/plain', status_int=500)
        return {'periphery_controller': periphery_controller}
        
