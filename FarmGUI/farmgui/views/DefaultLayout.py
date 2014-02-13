
from pyramid_layout.layout import layout_config

@layout_config(template='templates/layouts/default_layout.pt')
class DefaultLayout(object):
    '''
    '''
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def project_title(self):
        return 'Open Automated Farm'
