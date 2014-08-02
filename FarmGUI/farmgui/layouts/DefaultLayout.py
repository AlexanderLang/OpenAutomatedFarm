from pyramid_layout.layout import layout_config


@layout_config(name='default', template='farmgui:layouts/templates/default_layout.pt')
class DefaultLayout(object):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.additional_css = []
        self.additional_javascript = []

    @property
    def project_title(self):
        return 'Open Automated Farm'

    def add_css(self, css):
        self.additional_css.append(css)

    def add_javascript(self, js):
        self.additional_javascript.append(js)