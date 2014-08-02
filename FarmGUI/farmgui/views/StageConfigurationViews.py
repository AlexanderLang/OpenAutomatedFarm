from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError

from ..models import DBSession
from ..models import Stage
from ..models import Parameter
from ..models import StageConfiguration

from ..schemas import StageConfigurationSchema


class StageConfigurationViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='stage_configuration_new', renderer='farmgui:views/templates/stage_configuration_new.pt',
                 layout='default')
    def stage_configuration_new(self):
        add_form = Form(StageConfigurationSchema(), formid='addForm', buttons=('Save',), use_ajax=True)
        form = add_form.render()
        if 'Save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                stage = DBSession.query(Stage).filter(Stage.id == self.request.matchdict['_id']).first()
            except DBAPIError:
                return Response('database error (query Stage for id)', content_type='text/plain', status_int=500)
            try:
                vals = add_form.validate(controls)
                param = DBSession.query(Parameter).filter(Parameter.id == vals['parameter']).first()
                nsc = StageConfiguration(stage, param, vals['time'], vals['setpoint'], vals['upper_limit'],
                                         vals['lower_limit'])
                DBSession.add(nsc)
                return HTTPFound(location=self.request.route_url('stage_view', _id=stage.id))
            except ValidationFailure as e:
                form = e.render()
        return {'addForm': form}

    @view_config(route_name='stage_configurations_data', renderer='json')
    def stage_configurations_data(self):
        params = DBSession.query(Parameter).all()
        data = []
        for param in params:
            configs = DBSession.query(StageConfiguration)\
                .filter(StageConfiguration.stageId == self.request.matchdict['_id'])\
                .filter(StageConfiguration.parameterId == param.id).all()
            series = {'label': param.name,
                      'data': []}
            for conf in configs:
                t = conf.time.hour * 3600 + conf.time.minute * 60 + conf.time.second
                series['data'].append((t * 1000, conf.setpoint))
            data.append(series)
        return {'data': data}
