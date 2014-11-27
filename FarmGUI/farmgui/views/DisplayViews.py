import time
from time import mktime
from datetime import datetime
from datetime import timedelta
from pyramid.view import view_config
from sqlalchemy import asc
from sqlalchemy import desc
from deform_bootstrap import Form
from deform import ValidationFailure

from farmgui.models import DBSession
from farmgui.models import ParameterValueLog
from farmgui.models import ParameterSetpointLog
from farmgui.models import DeviceValueLog
from farmgui.models import DeviceSetpointLog
from farmgui.models import LogDiagram
from farmgui.models import ParameterLink
from farmgui.models import Parameter
from farmgui.models import Device
from farmgui.models import DeviceLink
from farmgui.models import Display

from farmgui.schemas import LogDiagramSchema
from farmgui.schemas import ParameterLinkSchema
from farmgui.schemas import DeviceLinkSchema


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
        layout.add_javascript(self.request.static_url('farmgui:static/js/redis_values.js'))
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
        new_parameter_link = ParameterLink(display, parameter, vals['target'], vals['color'])
        DBSession.add(new_parameter_link)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['parameter_link_panel'] = self.request.layout_manager.render_panel('parameter_link_panel', context=new_parameter_link)
        ret_dict['parameter_link'] = new_parameter_link.serialize
        return ret_dict

    @view_config(route_name='device_link_save', renderer='json')
    def device_link_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        dis_id = self.request.matchdict['dis_id']
        form = Form(DeviceLinkSchema().bind(),
                    formid='add_device_link_form_' + dis_id,
                    action=self.request.route_url('device_link_save', dis_id=dis_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rt, st, xhr, form) { add_device_link(rt);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        display = DBSession.query(Display).filter_by(_id=dis_id).one()
        device = DBSession.query(Device).filter_by(_id=vals['device']).one()
        new_device_link = DeviceLink(display, device, vals['target'], vals['color'])
        DBSession.add(new_device_link)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['device_link_panel'] = self.request.layout_manager.render_panel('device_link_panel', context=new_device_link)
        ret_dict['device_link'] = new_device_link.serialize
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
        pl.color = vals['color']
        ret_dict['parameter_link'] = pl.serialize
        ret_dict['parameter_link_name'] = pl.parameter.name + '-->' + pl.target
        return ret_dict

    @view_config(route_name='device_link_update', renderer='json')
    def device_link_update(self):
        ret_dict = {}
        dl_id = self.request.matchdict['dl_id']
        ret_dict['device_link_id'] = dl_id
        controls = self.request.POST.items()
        dl = DBSession.query(DeviceLink).filter_by(_id=dl_id).one()
        form = Form(DeviceLinkSchema().bind(device_link=dl),
                    formid='edit_device_link_' + dl_id,
                    action=self.request.route_url('device_link_update', dl_id=dl_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_device_link(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        dl.device_id = vals['device']
        dl.target = vals['target']
        dl.color = vals['color']
        ret_dict['device_link'] = dl.serialize
        ret_dict['device_link_name'] = dl.device.name + '-->' + dl.target
        return ret_dict

    @view_config(route_name='log_diagram_delete', renderer='json')
    def log_diagram_delete(self):
        log_diagram = DBSession.query(LogDiagram).filter_by(_id=self.request.matchdict['ld_id']).one()
        DBSession.delete(log_diagram)
        return {'delete': True}

    @view_config(route_name='parameter_link_delete', renderer='json')
    def parameter_link_delete(self):
        parameter_link = DBSession.query(ParameterLink).filter_by(_id=self.request.matchdict['pl_id']).one()
        DBSession.delete(parameter_link)
        return {'delete': True}

    @view_config(route_name='device_link_delete', renderer='json')
    def device_link_delete(self):
        device_link = DBSession.query(DeviceLink).filter_by(_id=self.request.matchdict['dl_id']).one()
        DBSession.delete(device_link)
        return {'delete': True}

    @view_config(route_name='log_diagram_data', renderer='json')
    def log_diagram_data(self):
        period = 0
        p_sp_ids = []
        p_va_ids = []
        d_sp_ids = []
        d_va_ids = []
        for i in self.request.POST.items():
            if i[0] == 'parameter_links':
                p_id, target = i[1].split(' ')
                if target == 'value':
                    p_va_ids.append(int(p_id))
                elif target == 'setpoint':
                    p_sp_ids.append(int(p_id))
                else:
                    print('error detecting parameter link target')
            elif i[0] == 'plot_period':
                period = int(i[1])
            elif i[0] == 'device_links':
                d_id, target = i[1].split(' ')
                if target == 'value':
                    d_va_ids.append(int(d_id))
                elif target == 'setpoint':
                    d_sp_ids.append(int(d_id))
                else:
                    print('error detecting device link target')
        now = datetime.now()
        start_time = now - timedelta(seconds=period)
        #utc_offset = time.altzone * 1000
        #now_millis = int(mktime(now.timetuple())) * 1000 - utc_offset
        now_millis = int(mktime(now.timetuple()))
        start_time_millis = now_millis - period*1000
        data = []
        for pid in p_va_ids:
            param = DBSession.query(Parameter).filter_by(_id=pid).one()
            logs = DBSession.query(ParameterValueLog).filter_by(parameter_id=pid).filter(
                ParameterValueLog.time >= start_time).order_by(asc(ParameterValueLog.time)).all()
            series_data = []
            for log in logs:
                #millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                millis = int(mktime(log.time.timetuple()) * 1000)
                series_data.append([millis, log.value])
            #print('series length: '+str(len(series)))
            data.append({'data': series_data, 'label': param.name + '-->value'})
        for pid in p_sp_ids:
            param = DBSession.query(Parameter).filter_by(_id=pid).one()
            logs_query = DBSession.query(ParameterSetpointLog).filter_by(parameter_id=pid).filter(
                ParameterSetpointLog.time >= start_time).order_by(asc(ParameterSetpointLog.time))
            logs = logs_query.all()
            series_data = []
            for log in logs:
                #millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                millis = int(mktime(log.time.timetuple()) * 1000)
                series_data.append([millis, log.setpoint])
            data.append({'data': series_data, 'label': param.name + '-->setpoint'})

        for did in d_va_ids:
            dev = DBSession.query(Device).filter_by(_id=did).one()
            logs = DBSession.query(DeviceValueLog).filter_by(device_id=did).filter(
                DeviceValueLog.time >= start_time).order_by(asc(DeviceValueLog.time)).all()
            series_data = []
            for log in logs:
                #millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                millis = int(mktime(log.time.timetuple()) * 1000)
                series_data.append([millis, log.value])
            #print('series length: '+str(len(series)))
            data.append({'data': series_data, 'label': dev.name + '-->value'})
        for did in d_sp_ids:
            dev = DBSession.query(Device).filter_by(_id=did).one()
            logs_query = DBSession.query(DeviceSetpointLog).filter_by(device_id=did).filter(
                DeviceSetpointLog.time >= start_time).order_by(asc(DeviceSetpointLog.time))
            logs = logs_query.all()
            series_data = []
            for log in logs:
                #millis = int(mktime(log.time.timetuple()) * 1000) - utc_offset
                millis = int(mktime(log.time.timetuple()) * 1000)
                series_data.append([millis, log.setpoint])
            data.append({'data': series_data, 'label': dev.name + '-->setpoint'})

        return {'xmin': start_time_millis,
                'xmax': now_millis,
                'data': data
        }