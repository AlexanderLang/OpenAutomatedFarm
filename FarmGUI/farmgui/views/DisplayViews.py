import time
from time import mktime
from datetime import datetime
from datetime import timedelta
from pyramid.view import view_config
from sqlalchemy import asc
from deform_bootstrap import Form
from deform import ValidationFailure

from farmgui.models import DBSession
from farmgui.models import ParameterValueLog
from farmgui.models import LogDiagram
from farmgui.models import ParameterLink
from farmgui.models import Parameter
from farmgui.models import Display

from farmgui.schemas import LogDiagramSchema
from farmgui.schemas import ParameterLinkSchema


class DisplayViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='display_views_home', renderer='templates/display_views_home.pt', layout='default')
    def display_views_home(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/display_functions.js'))
        layout.add_css(self.request.static_url('farmgui:static/css/plot_parameter.css'))

        add_log_diagram_form = Form(LogDiagramSchema().bind(),
                                    action=self.request.route_url('log_diagram_save'),
                                    formid='add_log_diagram_form',
                                    use_ajax=True,
                                    ajax_options='{"success": function (rText, sText, xhr, form) {'
                                                 'add_log_diagram(rText);}}',
                                    buttons=('Save',))
        log_diagrams = DBSession.query(LogDiagram).all()
        return {'log_diagrams': log_diagrams,
                'add_log_diagram_form': add_log_diagram_form.render()}

    @view_config(route_name='log_diagram_save', renderer='json')
    def log_diagram_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        form = Form(LogDiagramSchema().bind(),
                    formid='add_log_diagram_form',
                    action=self.request.route_url('log_diagram_save'),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { add_log_diagram(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        new_log_diagram = LogDiagram(vals['name'], vals['description'], vals['period'])
        DBSession.add(new_log_diagram)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['log_diagram_panel'] = self.request.layout_manager.render_panel('log_diagram_panel',
                                                                                 context=new_log_diagram)
        return ret_dict

    @view_config(route_name='log_diagram_update', renderer='json')
    def log_diagram_update(self):
        ret_dict = {}
        ld_id = self.request.matchdict['ld_id']
        ret_dict['log_diagram_id'] = ld_id
        controls = self.request.POST.items()
        ld = DBSession.query(LogDiagram).filter_by(_id=ld_id).one()
        form = Form(LogDiagramSchema().bind(log_diagram=ld),
                    formid='edit_log_diagram_' + ld_id,
                    action=self.request.route_url('log_diagram_update', ld_id=ld_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_log_diagram(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        ld.name = vals['name']
        ld.description = vals['description']
        ld.period = vals['period']
        ret_dict['log_diagram'] = ld.serialize
        return ret_dict

    @view_config(route_name='parameter_link_save', renderer='json')
    def parameter_link_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        dis_id = self.request.matchdict['dis_id']
        form = Form(ParameterLinkSchema().bind(),
                    formid='add_parameter_link_form_' + dis_id,
                    action=self.request.route_url('parameter_link_save', dis_id=dis_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { add_parameter_link(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        display = DBSession.query(Display).filter_by(_id=dis_id).one()
        parameter = DBSession.query(Parameter).filter_by(_id=vals['parameter']).one()
        new_parameter_link = ParameterLink(display, parameter, vals['target'])
        DBSession.add(new_parameter_link)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['parameter_link_panel'] = self.request.layout_manager.render_panel('parameter_link_panel', context=new_parameter_link)
        ret_dict['parameter_link'] = new_parameter_link.serialize
        return ret_dict

    @view_config(route_name='parameter_link_update', renderer='json')
    def parameter_link_update(self):
        ret_dict = {}
        pl_id = self.request.matchdict['pl_id']
        ret_dict['parameter_link_id'] = pl_id
        controls = self.request.POST.items()
        pl = DBSession.query(ParameterLink).filter_by(_id=pl_id).one()
        form = Form(ParameterLinkSchema().bind(parameter_link=pl),
                    formid='edit_parameter_link_' + pl_id,
                    action=self.request.route_url('parameter_link_update', pl_id=pl_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_parameter_link(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        pl.parameter_id = vals['parameter']
        pl.target = vals['target']
        ret_dict['parameter_link'] = pl.serialize
        ret_dict['parameter_link_name'] = pl.parameter.name + '--&gt;' + pl.target
        return ret_dict

    @view_config(route_name='log_diagram_delete', renderer='json')
    def log_diagram_delete(self):
        log_diagram = DBSession.query(LogDiagram).filter_by(_id=self.request.matchdict['ld_id']).first()
        DBSession.delete(log_diagram)
        return {'delete': True}

    @view_config(route_name='parameter_link_delete', renderer='json')
    def parameter_link_delete(self):
        parameter_link = DBSession.query(ParameterLink).filter_by(_id=self.request.matchdict['pl_id']).first()
        DBSession.delete(parameter_link)
        return {'delete': True}

    @view_config(route_name='log_diagram_data', renderer='json')
    def log_diagram_data(self):
        period = 0
        p_ids = []
        for i in self.request.POST.items():
            if i[0] == 'parameter_ids':
                p_ids.append(i[1])
            elif i[0] == 'plot_period':
                period = int(i[1])
        now = datetime.now()
        #print('period: '+str(period)+' s')
        start_time = now - timedelta(seconds=period)
        utc_offset = time.altzone * 1000
        now_millis = int(mktime(now.timetuple())) * 1000 - utc_offset
        start_time_millis = now_millis - period*1000
        data = []
        for pid in p_ids:
            logs = DBSession.query(ParameterValueLog).filter_by(parameter_id=pid).filter(
                ParameterValueLog.time >= start_time).order_by(asc(ParameterValueLog.time)).all()
            series = []
            for log in logs:
                millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                series.append([millis, log.value])
            #print('series length: '+str(len(series)))
            data.append(series)
        return {'xmin': start_time_millis,
                'xmax': now_millis,
                'data': data
        }