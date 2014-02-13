
from pyramid.view import view_config

class ProjectViews(object):
    '''
    general views
    '''
    
    def __init__(self, request):
        self.request = request
    
    @view_config(route_name='home', renderer='templates/home.pt')
    def home_view(self):
        return {"page_title": "Home"}
    
    @view_config(route_name='about', renderer='templates/about.pt')
    def about_view(self):
        return {}