
from pyramid.view import view_config

class ProjectViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='home_view', renderer='templates/home.pt', layout='default')
    def home_view(self):
        return {"page_title": "Home"}
    
    @view_config(route_name='about_view', renderer='templates/about.pt', layout='default')
    def about_view(self):
        return {}