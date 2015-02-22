from deform import ValidationFailure
from deform_bootstrap import Form
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from sqlalchemy import desc

from farmgui.models import DBSession
from farmgui.models import InterpolationKnot
from farmgui.models import Parameter
from farmgui.models import Device
from farmgui.models import CalendarEntry
from farmgui.models import DeviceCalendarEntry
from farmgui.models import SetpointInterpolation

from farmgui.schemas import CalendarEntrySchema
from farmgui.schemas import SetpointInterpolationSchema
from farmgui.schemas import InterpolationKnotSchema
from sqlalchemy.exc import DBAPIError


class CalendarViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='calendar_param_home', renderer='templates/calendar_param_home.pt', layout='default')
    def calendar_param_home(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        param = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['param_id']).one()
        interpolations = DBSession.query(SetpointInterpolation).all()
        calendar_schema = CalendarEntrySchema().bind()
        add_calendar_form = Form(calendar_schema,
                                 action=self.request.route_url('calendar_param_entry_save', param_id=param.id),
                                 formid='add_calendar_entry_form',
                                 buttons=('Save',))
        interpolation_schema = SetpointInterpolationSchema().bind()
        add_interpolation_form = Form(interpolation_schema,
                                      action=self.request.route_url('interpolation_save'),
                                      formid='add_interpolation_form',
                                      buttons=('Save',))
        return {'parameter': param,
                'calendar': param.calendar,
                'interpolations': interpolations,
                'add_calendar_entry_form': add_calendar_form.render(),
                'add_interpolation_form': add_interpolation_form.render()}

    @view_config(route_name='calendar_dev_home', renderer='templates/calendar_dev_home.pt', layout='default')
    def calendar_dev_home(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/jquery.flot.time.js'))
        dev = DBSession.query(Device).filter_by(_id=self.request.matchdict['dev_id']).one()
        interpolations = DBSession.query(SetpointInterpolation).all()
        calendar_schema = CalendarEntrySchema().bind()
        add_calendar_form = Form(calendar_schema,
                                 action=self.request.route_url('calendar_dev_entry_save', dev_id=dev.id),
                                 formid='add_calendar_entry_form',
                                 buttons=('Save',))
        interpolation_schema = SetpointInterpolationSchema().bind()
        add_interpolation_form = Form(interpolation_schema,
                                      action=self.request.route_url('interpolation_save'),
                                      formid='add_interpolation_form',
                                      buttons=('Save',))
        return {"page_title": dev.name + " Calendar",
                'calendar': dev.calendar,
                'interpolations': interpolations,
                'add_calendar_entry_form': add_calendar_form.render(),
                'add_interpolation_form': add_interpolation_form.render()}

    @view_config(route_name='calendar_param_entry_save', renderer='json')
    def calendar_param_entry_save(self):
        """
        save new calendar entry
        """
        ret_dict = {}
        controls = self.request.POST.items()
        param = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['param_id']).one()
        last_entry = DBSession.query(CalendarEntry).filter_by(parameter_id=param.id).order_by(
            desc(CalendarEntry.entry_number)).first()
        add_form = Form(CalendarEntrySchema().bind(),
                        formid='add_param_calender_entry',
                        action=self.request.route_url('calendar_param_entry_save', param_id=param.id),
                        use_ajax=True,
                        ajax_options='{"success": function(rt, st, xhr, form) { add_calendar_param_entry(rt);}}',
                        buttons=('Save',))
        try:
            vals = add_form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        inter = DBSession.query(SetpointInterpolation).filter_by(_id=vals['interpolation']).one()
        index = 1
        if last_entry is not None:
            index = last_entry.entry_number + 1
        new_entry = CalendarEntry(param, index, inter)
        DBSession.add(new_entry)
        DBSession.flush()
        ret_dict['form'] = add_form.render()
        ret_dict['entry_panel'] = self.request.layout_manager.render_panel('calendar_param_entry', context=new_entry)
        self.request.redis.publish('calendar_changes', 'param ' + str(param.id))
        return ret_dict

    @view_config(route_name='calendar_param_entry_delete', renderer='json')
    def calendar_param_entry_delete(self):
        entry_id = self.request.matchdict['entry_id']
        entry = DBSession.query(CalendarEntry).filter_by(_id=entry_id).one()
        self.request.redis.publish('calendar_changes', 'removed ' + str(entry_id))
        DBSession.delete(entry)
        return {'delete': True}

    @view_config(route_name='calendar_dev_entry_save', renderer='json')
    def calendar_dev_entry_save(self):
        """
        save new calendar entry
        """
        ret_dict = {}
        controls = self.request.POST.items()
        dev = DBSession.query(Device).filter_by(_id=self.request.matchdict['dev_id']).one()
        last_entry = DBSession.query(DeviceCalendarEntry).filter_by(device_id=dev.id).order_by(
            desc(DeviceCalendarEntry.entry_number)).first()
        add_form = Form(CalendarEntrySchema().bind(),
                        formid='add_dev_calender_entry',
                        action=self.request.route_url('calendar_dev_entry_save', dev_id=dev.id),
                        use_ajax=True,
                        ajax_options='{"success": function(rt, st, xhr, form) { add_calendar_dev_entry(rt);}}',
                        buttons=('Save',))
        try:
            vals = add_form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        inter = DBSession.query(SetpointInterpolation).filter_by(_id=vals['interpolation']).one()
        if last_entry is not None:
            new_entry = DeviceCalendarEntry(dev, last_entry.entry_number + 1, inter)
        else:
            new_entry = DeviceCalendarEntry(dev, 1, inter)
        DBSession.add(new_entry)
        DBSession.flush()
        ret_dict['form'] = add_form.render()
        ret_dict['entry_panel'] = self.request.layout_manager.render_panel('calendar_dev_entry', context=new_entry)
        self.request.redis.publish('calendar_changes', 'dev ' + str(dev.id))
        return ret_dict

    @view_config(route_name='calendar_dev_entry_delete', renderer='json')
    def calendar_dev_entry_delete(self):
        entry_id = self.request.matchdict['entry_id']
        entry = DBSession.query(DeviceCalendarEntry).filter_by(_id=entry_id).one()
        self.request.redis.publish('calendar_changes', 'removed ' + str(entry_id))
        DBSession.delete(entry)
        return {'delete': True}

    @view_config(route_name='interpolation_save', renderer='json')
    def interpolation_save(self):
        """
        save new setpoint interpolation
        """
        ret_dict = {}
        controls = self.request.POST.items()
        add_form = Form(SetpointInterpolationSchema().bind(),
                        formid='add_interpolation_form',
                        action=self.request.route_url('interpolation_save'),
                        use_ajax=True,
                        ajax_options='{"success": function(rText, sText, xhr, form) { add_interpolation(rText);}}',
                        buttons=('Save',))
        try:
            vals = add_form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        new_inter = SetpointInterpolation(vals['name'], vals['order'], vals['start_value'], vals['end_time'],
                                          vals['end_value'], vals['description'])
        DBSession.add(new_inter)
        DBSession.flush()
        ret_dict['form'] = add_form.render()
        ret_dict['interpolation_panel'] = self.request.layout_manager.render_panel('interpolation_panel',
                                                                                   context=new_inter)
        filename = self.request.registry.settings['plot_directory'] + '/interpolation_' + str(new_inter.id) + '.png'
        new_inter.plot('', filename)
        self.request.redis.publish('calendar_changes', 'interpolation saved')
        return ret_dict

    @view_config(route_name='interpolation_update', renderer='json')
    def interpolation_update(self):
        try:
            spip = DBSession.query(SetpointInterpolation).filter_by(
                _id=self.request.matchdict['interpolation_id']).first()
        except DBAPIError:
            return Response('database error (query SetpointInterpolation)', content_type='text/plain', status_int=500)
        form = Form(SetpointInterpolationSchema().bind(interpolation=spip), buttons=('Save',))
        controls = self.request.POST
        controls['name'] = spip.name
        try:
            values = form.validate(controls.items())
        except ValidationFailure as e:
            return {'error_form': e.render()}
        spip.name = values['name']
        spip.order = values['order']
        spip.start_value = values['start_value']
        spip.end_time = values['end_time']
        spip.end_value = values['end_value']
        spip.description = values['description']
        filename = self.request.registry.settings['plot_directory'] + '/interpolation_' + str(spip.id) + '.png'
        spip.plot('', filename)
        self.request.redis.publish('calendar_changes', 'interpolation changed')
        return HTTPFound(
            location=self.request.route_url('calendar_home', parameter_id=self.request.matchdict['parameter_id']))

    @view_config(route_name='interpolation_delete')
    def interpolation_delete(self):
        interpolation = DBSession.query(SetpointInterpolation).filter_by(
            _id=self.request.matchdict['interpolation_id']).first()
        DBSession.delete(interpolation)
        self.request.redis.publish('calendar_changes', 'interpolation deleted')
        return HTTPFound(
            location=self.request.route_url('calendar_home', parameter_id=self.request.matchdict['parameter_id']))

    @view_config(route_name='interpolation_knot_save', renderer='templates/error_form.pt', layout='default')
    def interpolation_knot_save(self):
        controls = self.request.POST
        param = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['parameter_id']).first()
        inter = DBSession.query(SetpointInterpolation).filter_by(_id=self.request.matchdict['interpolation_id']).first()
        add_form = Form(InterpolationKnotSchema().bind())
        try:
            p = add_form.validate(controls.items())
            new_inter = InterpolationKnot(inter, p['time'], p['value'])
            DBSession.add(new_inter)
        except ValidationFailure as e:
            return {'error_form': e.render()}
        filename = self.request.registry.settings['plot_directory'] + '/interpolation_' + str(inter.id) + '.png'
        inter.plot('', filename)
        return HTTPFound(location=self.request.route_url('calendar_home', parameter_id=param.id))

    @view_config(route_name='interpolation_knot_update', renderer='json')
    def interpolation_knot_update(self):
        ret_dict = {}
        try:
            knot = DBSession.query(InterpolationKnot).filter_by(_id=self.request.matchdict['knot_id']).first()
            inter = DBSession.query(SetpointInterpolation).filter_by(
                _id=self.request.matchdict['inter_id']).first()
        except DBAPIError:
            return Response('database error (query InterpolationKnot)', content_type='text/plain', status_int=500)
        form = Form(InterpolationKnotSchema().bind(knot=knot), buttons=('Save',))
        controls = self.request.POST
        controls['interpolation_id'] = inter.id
        try:
            values = form.validate(controls.items())
        except ValidationFailure as e:
            return {'error_form': e.render()}
        knot.time = values['time']
        knot.value = values['value']
        filename = self.request.registry.settings['plot_directory'] + '/interpolation_' + str(inter.id) + '.png'
        inter.plot('', filename)
        self.request.redis.publish('parameter_changes', 'interpolation changed')
        ret_dict['form'] = form.render()
        ret_dict['knot_panel'] = self.request.layout_manager.render_panel('interpolation_knot_panel', context=knot)
        return ret_dict

    @view_config(route_name='interpolation_knot_delete', renderer='json')
    def interpolation_knot_delete(self):
        interpolation_knot = DBSession.query(InterpolationKnot).filter_by(_id=self.request.matchdict['knot_id']).first()
        DBSession.delete(interpolation_knot)
        return {'delete': True}
