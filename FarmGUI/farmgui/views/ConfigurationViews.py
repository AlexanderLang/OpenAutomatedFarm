from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError, IntegrityError

from json import dump

from ..models import DBSession
from ..models import serialize
from ..models import FarmComponent
from ..models import Parameter
from ..models import ParameterType
from ..models import Sensor
from ..models import FieldSetting
from ..models import PeripheryController
from ..models import Device
from ..models import DeviceType
from ..models import Actuator
from ..models import Regulator
from ..models import RegulatorType
from ..models import RegulatorConfig

from ..schemas import FarmComponentSchema
from ..schemas import PeripheryControllerSchema
from ..schemas import ParameterSchema
from ..schemas import FieldSettingSchema
from ..schemas import DeviceSchema
from ..schemas import RegulatorSchema
from ..schemas import RegulatorConfigSchema


class ConfigurationViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='configuration_views_home')
    def configuration_views_home(self):
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='field_settings_list', renderer='farmgui:views/templates/field_settings_list.pt',
                 layout='default')
    def field_settings_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            field_settings = DBSession.query(FieldSetting).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'field_settings': field_settings}

    @view_config(route_name='field_setting_update')
    def field_setting_update(self):
        try:
            fs = DBSession.query(FieldSetting).filter_by(name=self.request.matchdict['name']).first()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        form = Form(FieldSettingSchema(), buttons=('Save',))
        controls = self.request.POST
        controls['name'] = fs.name
        controls['description'] = fs.description
        controls = controls.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        fs.value = values['value']
        return HTTPFound(location=self.request.route_url('field_settings_list'))

    @view_config(route_name='components_list', renderer='farmgui:views/templates/components_list.pt', layout='default')
    def components_list(self):
        layout = self.request.layout_manager.layout
        #layout.add_css(self.request.static_url('deform_bootstrap:static/deform_bootstrap.css'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        add_form = Form(FarmComponentSchema(),
                        formid='add_component_form',
                        action=self.request.route_url('component_save', comp_id=0),
                        use_ajax=True,
                        ajax_options='{"success": function (rText, sText, xhr, form) {'
                                     '  add_component(rText, sText, xhr, form);}}',
                        buttons=('Save',))
        try:
            components = DBSession.query(FarmComponent).all()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        return {'components': components,
                'add_component_form': add_form.render()}

    @view_config(route_name='component_save', renderer='json')
    def component_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        comp_id = self.request.matchdict['comp_id']
        if comp_id == '0':
            # new component
            form_id = 'add_component_form'
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '  add_component(rText, sText, xhr, form);}}'
        else:
            # existing component
            comp = DBSession.query(FarmComponent).filter_by(_id=self.request.matchdict['comp_id']).first()
            form_id = 'edit_component_form_'+str(comp.id)
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '  edit_component(rText, sText, xhr, form);}}'
        form = Form(FarmComponentSchema(),
                        formid=form_id,
                        action=self.request.route_url('component_save', comp_id=0),
                        use_ajax=True,
                        ajax_options= form_opt,
                        buttons=('Save',))
        try:
            values = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict

        if comp_id == '0':
            # new component
            try:
                new_component = FarmComponent(values['name'], values['description'])
                DBSession.add(new_component)
                DBSession.flush()
                ret_dict['component'] = self.request.layout_manager.render_panel('component_panel', new_component)
            except IntegrityError:
                ret_dict['error'] = True
                ret_dict['error_msg'] = 'Error: a component with this name already exists'
        else:
            # existing component
            try:
                comp.name = values['name']
                comp.description = values['description']
                ret_dict['form'] = form.render(component=comp)
                ret_dict['component'] = serialize(comp)
            except IntegrityError:
                ret_dict['error'] = True
                ret_dict['error_msg'] = 'Error: a component with this name already exists'

        return ret_dict

    @view_config(route_name='component_delete')
    def component_delete(self):
        comp = DBSession.query(FarmComponent).filter_by(_id=self.request.matchdict['comp_id']).first()
        DBSession.delete(comp)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='parameter_save', renderer='json')
    def parameter_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        param_id = self.request.matchdict['param_id']
        comp_id = self.request.matchdict['comp_id']
        ret_dict['comp_id'] = comp_id
        if param_id != '0':
            # existing component
            param = DBSession.query(Parameter).filter_by(_id=param_id).first()
            form_id = 'edit_parameter_form_' + comp_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '  edit_parameter(rText, sText, xhr, form);}}'
        else:
            # new parameter
            form_id = 'add_parameter_form_' + comp_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '  add_parameter(rText, sText, xhr, form);}}'
        form = Form(ParameterSchema().bind(),
                            formid=form_id,
                            action=self.request.route_url('parameter_save', comp_id=comp_id, param_id=param_id),
                            use_ajax=True,
                            ajax_options=form_opt,
                            buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict

        if param_id == '0':
            comp = DBSession.query(FarmComponent).filter_by(_id=comp_id).first()
            parameter_type = DBSession.query(ParameterType).filter_by(_id=vals['parameter_type']).first()
            sensor = DBSession.query(Sensor).filter_by(_id=vals['sensor']).first()
            new_parameter = Parameter(comp, vals['name'], parameter_type, vals['interval'], sensor, vals['description'])
            DBSession.add(new_parameter)
            DBSession.flush()
            ret_dict['parameter_panel'] = self.request.layout_manager.render_panel('parameter_panel', new_parameter)
        else:
            param.name = vals['name']
            param.parameter_type_id = vals['parameter_type']
            param.interval = vals['interval']
            param.sensor_id = vals['sensor']
            param.description = vals['description']
            ret_dict['form'] = form.render(parameter=param)
            ret_dict['parameter'] = param.serialize
        self.request.redis.publish('parameter_changes', 'parameter changed')
        return ret_dict

    @view_config(route_name='parameter_delete')
    def parameter_delete(self):
        parameter = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['param_id']).first()
        DBSession.delete(parameter)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='device_save', renderer='json')
    def device_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        dev_id = self.request.matchdict['dev_id']
        comp_id = self.request.matchdict['comp_id']
        ret_dict['comp_id'] = comp_id
        if dev_id != '0':
            # existing device
            dev = DBSession.query(Device).filter_by(_id=dev_id).first()
            form_id = 'edit_device_form_' + dev_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '   edit_device(rText, sText, xhr, form);}}'
        else:
            # new device
            form_id = 'add_device_form_' + comp_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '  add_device(rText, sText, xhr, form);}}'
        form = Form(DeviceSchema().bind(),
                    formid=form_id,
                    action=self.request.route_url('device_save', comp_id=comp_id, dev_id=dev_id),
                    use_ajax=True,
                    ajax_options=form_opt,
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict

        if dev_id == '0':
            comp = DBSession.query(FarmComponent).filter_by(_id=comp_id).first()
            device_type = DBSession.query(DeviceType).filter_by(_id=vals['device_type']).first()
            actuator = DBSession.query(Actuator).filter_by(_id=vals['actuator']).first()
            new_dev = Device(comp, vals['name'], device_type, actuator, vals['description'])
            DBSession.add(new_dev)
            DBSession.flush()
            ret_dict['device_panel'] = self.request.layout_manager.render_panel('device_panel', new_dev)
        else:
            dev.name = vals['name']
            dev.device_type_id = vals['device_type']
            dev.actuator_id = vals['actuator']
            dev.description = vals['description']
            ret_dict['form'] = form.render(device=dev)
            ret_dict['device'] = dev.serialize
        self.request.redis.publish('device_changes', 'device changed')
        return ret_dict

    @view_config(route_name='device_delete')
    def device_delete(self):
        device = DBSession.query(Device).filter_by(_id=self.request.matchdict['dev_id']).first()
        DBSession.delete(device)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='regulator_save', renderer='json')
    def regulator_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        reg_id = self.request.matchdict['reg_id']
        comp_id = self.request.matchdict['comp_id']
        ret_dict['comp_id'] = comp_id
        if reg_id != '0':
            # existing regulator
            reg = DBSession.query(Regulator).filter_by(_id=reg_id).first()
            form_id = 'edit_regulator_form_' + reg_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '    edit_regulator(rText, sText, xhr, form);}}'
        else:
            # new regulator
            form_id = 'add_regulator_form_' + comp_id
            form_opt = '{"success": function (rText, sText, xhr, form) {' \
                       '    add_regulator(rText, sText, xhr, form);}}'
        form = Form(RegulatorSchema().bind(),
                    formid=form_id,
                    action=self.request.route_url('regulator_save', comp_id=comp_id, reg_id=reg_id),
                    use_ajax=True,
                    ajax_options=form_opt,
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict

        if reg_id == '0':
            # new regulator
            comp = DBSession.query(FarmComponent).filter_by(_id=comp_id).first()
            regulator_type = DBSession.query(RegulatorType).filter_by(_id=vals['regulator_type']).first()
            parameter = DBSession.query(Parameter).filter_by(_id=vals['parameter']).first()
            device = DBSession.query(Device).filter_by(_id=vals['device']).first()
            new_reg = Regulator(comp, vals['name'], regulator_type, parameter, device, vals['description'])
            DBSession.add(new_reg)
            DBSession.flush()
            ret_dict['regulator_panel'] = self.request.layout_manager.render_panel('regulator_panel', new_reg)
        else:
            reg.name = vals['name']
            reg.regulator_type_id = vals['regulator_type']
            reg.input_parameter_id = vals['parameter']
            reg.output_device_id = vals['device']
            reg.description = vals['description']
            ret_dict['form'] = form.render(regulator=reg)
            ret_dict['regulator'] = reg.serialize

        self.request.redis.publish('regulator_changes', 'new regulator')
        return ret_dict

    @view_config(route_name='regulator_delete')
    def regulator_delete(self):
        regulator = DBSession.query(Regulator).filter_by(_id=self.request.matchdict['reg_id']).first()
        DBSession.delete(regulator)
        return HTTPFound(location=self.request.route_url('components_list'))

    @view_config(route_name='regulator_config_update', renderer='json')
    def regulator_config_update(self):
        ret_dict = {}
        reg_id = self.request.matchdict['reg_id']
        ret_dict['regulator_id'] = reg_id
        conf_id = self.request.matchdict['_id']
        ret_dict['regulator_config_id'] = conf_id
        controls = self.request.POST.items()
        rc = DBSession.query(RegulatorConfig).filter_by(_id=conf_id).first()
        form = Form(RegulatorConfigSchema().bind(),
                    formid='edit_regulator_' + reg_id + '_config_form_' + conf_id,
                    action=self.request.route_url('regulator_config_update', reg_id=reg_id, _id=conf_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {' \
                                 '    edit_regulator_config(rText, sText, xhr, form);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        rc.value = vals['value']
        ret_dict['regulator_config'] = serialize(rc)
        self.request.redis.publish('regulator_changes', 'regulator config changed')
        return ret_dict

    @view_config(route_name='periphery_controllers_list',
                 renderer='farmgui:views/templates/periphery_controllers_list.pt', layout='default')
    def periphery_controllers_list(self):
        layout = self.request.layout_manager.layout
        layout.add_javascript(self.request.static_url('farmgui:static/js/configuration_views.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))
        try:
            periphery_controllers = DBSession.query(PeripheryController).all()
        except DBAPIError:
            return Response('database error (query PeripheryControllers)', content_type='text/plain', status_int=500)
        return {'periphery_controllers': periphery_controllers}

    @view_config(route_name='periphery_controller_update')
    def periphery_controller_update(self):
        try:
            pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['_id']).first()
        except DBAPIError:
            return Response('database error (query FieldSettings)', content_type='text/plain', status_int=500)
        form = Form(PeripheryControllerSchema(), buttons=('Save',))
        controls = self.request.POST.items()
        try:
            values = form.validate(controls)
        except ValidationFailure as e:
            return Response(e.render())
        pc.name = values['name']
        return HTTPFound(location=self.request.route_url('periphery_controllers_list'))

    @view_config(route_name='periphery_controller_delete')
    def periphery_controller_delete(self):
        pc = DBSession.query(PeripheryController).filter_by(_id=self.request.matchdict['_id']).first()
        DBSession.delete(pc)
        return HTTPFound(location=self.request.route_url('periphery_controllers_list'))
