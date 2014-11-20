from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


class ProjectViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='project_views_home', renderer='templates/home.pt', layout='default')
    def home_view(self):
        return {"page_title": "Home"}

    @view_config(route_name='project_views_about', renderer='templates/about.pt', layout='default')
    def about_view(self):
        return {}

    @view_config(route_name='get_redis_values', renderer='json')
    def get_redis_value(self):
        ret_dict = {}
        for item in self.request.POST.items():
            key = item[1]
            raw = self.request.redis.get(key)
            if raw is None:
                ret_dict[key] = 'error'
            else:
                ret_dict[key] = raw.decode('utf-8')
        return ret_dict