from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


class ProjectViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='project_views_root')
    def root_view(self):
        return HTTPFound(location=self.request.route_url('project_views_home'))

    @view_config(route_name='project_views_home', renderer='templates/home.pt', layout='default')
    def home_view(self):
        return {"page_title": "Home"}

    @view_config(route_name='project_views_about', renderer='templates/about.pt', layout='default')
    def about_view(self):
        return {}