from pyramid.view import view_config
from pyramid.response import Response

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models import PeripheryController


class PeripheryControllerViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    def periphery_controller_view(self):
        try:
            periphery_controller = DBSession.query(PeripheryController).filter(
                PeripheryController.id == self.request.matchdict['_id']).first()
            if 'save' in self.request.POST:
                periphery_controller.name = self.request.POST.get('name')
        except DBAPIError:
            return Response('database error (query PeripheryControllers for id)', content_type='text/plain',
                            status_int=500)
        return {'periphery_controller': periphery_controller}