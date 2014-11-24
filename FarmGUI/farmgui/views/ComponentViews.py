from pyramid.view import view_config
from deform_bootstrap import Form
from deform import ValidationFailure

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import IntegrityError

from farmgui.models import DBSession
from farmgui.models import Parameter
from farmgui.models import ParameterType
from farmgui.models import Sensor
from farmgui.models import Device
from farmgui.models import DeviceType
from farmgui.models import Actuator
from farmgui.models import Regulator
from farmgui.models import Component
from farmgui.models import ComponentInput
from farmgui.models import ComponentProperty

from farmgui.schemas import ComponentSchema
from farmgui.schemas import EditParameterSchema
from farmgui.schemas import NewParameterSchema
from farmgui.schemas import EditDeviceSchema
from farmgui.schemas import NewDeviceSchema
from farmgui.schemas import EditRegulatorSchema
from farmgui.schemas import NewRegulatorSchema
from farmgui.schemas import ComponentInputSchema
from farmgui.schemas import ComponentPropertySchema

from farmgui.regulators import regulator_factory


class ComponentViews(object):
    """
    general views
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='component_views_home',
                 renderer='farmgui:views/templates/component_views_home.pt',
                 layout='default')
    def component_views_home(self):
        layout = self.request.layout_manager.layout
        # layout.add_css(self.request.static_url('deform_bootstrap:static/deform_bootstrap.css'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/component_functions.js'))
        layout.add_javascript(self.request.static_url('farmgui:static/js/redis_values.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/deform.js'))
        layout.add_javascript(self.request.static_url('deform:static/scripts/jquery.form.js'))

        add_parameter_form = Form(NewParameterSchema().bind(),
                                  action=self.request.route_url('parameter_save'),
                                  formid='add_parameter_form',
                                  use_ajax=True,
                                  ajax_options='{"success": function (rText, sText, xhr, form) {'
                                               'add_parameter(rText);}}',
                                  buttons=('Save',))
        add_device_form = Form(NewDeviceSchema().bind(),
                               action=self.request.route_url('device_save'),
                               formid='add_device_form',
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            'add_device(rText);}}',
                               buttons=('Save',))
        add_regulator_form = Form(NewRegulatorSchema().bind(),
                                  action=self.request.route_url('regulator_save'),
                                  formid='add_regulator_form',
                                  use_ajax=True,
                                  ajax_options='{"success": function (rText, sText, xhr, form) {'
                                               'add_regulator(rText);}}',
                                  buttons=('Save',))
        parameters = DBSession.query(Parameter).all()
        devices = DBSession.query(Device).all()
        regulators = DBSession.query(Regulator).all()
        return {'parameters': parameters,
                'devices': devices,
                'regulators': regulators,
                'add_parameter_form': add_parameter_form.render(),
                'add_device_form': add_device_form.render(),
                'add_regulator_form': add_regulator_form.render()}

    @view_config(route_name='component_update', renderer='json')
    def component_update(self):
        ret_dict = {}
        controls = self.request.POST.items()
        comp_id = self.request.matchdict['comp_id']
        comp = DBSession.query(Component).filter_by(_id=comp_id).one()
        form = Form(ComponentSchema().bind(),
                    formid='edit_component_form_' + comp_id,
                    action=self.request.route_url('component_update', comp_id=comp_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_component(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['component'] = comp.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        comp.name = vals['name']
        comp.description = vals['description']
        ret_dict['form'] = form.render(component=comp)
        ret_dict['component'] = comp.serialize
        self.request.redis.publish('component_changes', 'changed '+str(comp_id))
        return ret_dict

    @view_config(route_name='component_delete', renderer='json')
    def component_delete(self):
        comp_id = self.request.matchdict['comp_id']
        component = DBSession.query(Component).filter_by(_id=comp_id).one()
        channel = component.component_type + '_changes'
        DBSession.delete(component)
        self.request.redis.publish(channel, 'deleted '+str(comp_id))
        return {'delete': True}

    @view_config(route_name='component_input_update', renderer='json')
    def component_input_update(self):
        ret_dict = {}
        controls = self.request.POST.items()
        comp_in_id = self.request.matchdict['comp_in_id']
        comp_in = DBSession.query(ComponentInput).filter_by(_id=comp_in_id).one()
        form = Form(ComponentInputSchema().bind(),
                    formid='edit_component_input_form_' + comp_in_id,
                    action=self.request.route_url('component_input_update', comp_in_id=comp_in_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_component_input(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['component_input'] = comp_in.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        comp_in.connected_output_id = vals['connected_output']
        ret_dict['form'] = form.render(component_input=comp_in)
        ret_dict['component_input'] = comp_in.serialize
        connected_output_name = 'not connected'
        if comp_in.connected_output is not None:
            connected_output_name = comp_in.connected_output.component.name + ': ' + comp_in.connected_output.name
        ret_dict['connected_output_name'] = connected_output_name
        self.request.redis.publish('component_input_changes', str(comp_in_id))
        return ret_dict

    @view_config(route_name='parameter_save', renderer='json')
    def parameter_save(self):
        """
        save new parameter
        """
        ret_dict = {}
        controls = self.request.POST.items()
        form = Form(NewParameterSchema().bind(),
                    formid='add_parameter_form',
                    action=self.request.route_url('parameter_save'),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { add_parameter(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['form'] = e.render()
            return ret_dict
        parameter_type = DBSession.query(ParameterType).filter_by(_id=vals['parameter_type']).one()
        new_parameter = Parameter(vals['name'], parameter_type, None, vals['description'])
        DBSession.add(new_parameter)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['parameter_panel'] = self.request.layout_manager.render_panel('parameter_panel', context=new_parameter)
        self.request.redis.publish('parameter_changes', 'added '+str(new_parameter.id))
        return ret_dict

    @view_config(route_name='parameter_update', renderer='json')
    def parameter_update(self):
        ret_dict = {}
        if self.request.POST['sensor'] == 'None':
            self.request.POST['sensor'] = None
        controls = self.request.POST.items()
        param_id = self.request.matchdict['param_id']
        param = DBSession.query(Parameter).filter_by(_id=param_id).one()
        form = Form(EditParameterSchema().bind(parameter=param),
                    formid='edit_parameter_form_' + param_id,
                    action=self.request.route_url('parameter_update', param_id=param_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_parameter(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['parameter'] = param.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        if vals['sensor'] is not None:
            param.sensor = DBSession.query(Sensor).filter_by(_id=vals['sensor']).one()
        else:
            param.sensor = None
        ret_dict['form'] = form.render(parameter=param)
        ret_dict['parameter'] = param.serialize
        self.request.redis.publish('parameter_changes', 'changed ' + str(param.id))
        return ret_dict

    @view_config(route_name='parameter_delete', renderer='json')
    def parameter_delete(self):
        parameter = DBSession.query(Parameter).filter_by(_id=self.request.matchdict['param_id']).first()
        DBSession.delete(parameter)
        self.request.redis.publish('parameter_changes', 'removed ' + str(parameter.id))
        return {'delete': True}

    @view_config(route_name='device_save', renderer='json')
    def device_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        form = Form(NewDeviceSchema().bind(),
                    formid='add_device_form',
                    action=self.request.route_url('device_save'),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { add_device(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        device_type = DBSession.query(DeviceType).filter_by(_id=vals['device_type']).one()
        new_dev = Device(vals['name'], device_type, None, vals['description'])
        DBSession.add(new_dev)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['device_panel'] = self.request.layout_manager.render_panel('device_panel', context=new_dev)
        self.request.redis.publish('device_changes', 'added '+str(new_dev.id))
        return ret_dict

    @view_config(route_name='device_update', renderer='json')
    def device_update(self):
        ret_dict = {}
        if self.request.POST['actuator'] == 'None':
            self.request.POST['actuator'] = None
        controls = self.request.POST.items()
        dev_id = self.request.matchdict['dev_id']
        dev = DBSession.query(Device).filter_by(_id=dev_id).one()
        form = Form(EditDeviceSchema().bind(device=dev),
                    formid='edit_device_form_' + dev_id,
                    action=self.request.route_url('device_update', dev_id=dev_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_device(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['device'] = dev.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        if vals['actuator'] is not None:
            dev.actuator = DBSession.query(Actuator).filter_by(_id=vals['actuator']).one()
        else:
            dev.actuator = None
        ret_dict['form'] = form.render(device=dev)
        ret_dict['device'] = dev.serialize
        self.request.redis.publish('device_changes', 'changed '+str(dev.id))
        return ret_dict

    @view_config(route_name='device_delete', renderer='json')
    def device_delete(self):
        device = DBSession.query(Device).filter_by(_id=self.request.matchdict['dev_id']).one()
        dev_id = device.id
        DBSession.delete(device)
        self.request.redis.publish('device_changes', 'removed '+str(dev_id))
        return {'delete': True}

    @view_config(route_name='regulator_save', renderer='json')
    def regulator_save(self):
        ret_dict = {}
        controls = self.request.POST.items()
        form = Form(NewRegulatorSchema().bind(),
                    formid='add_regulator_form',
                    action=self.request.route_url('regulator_save'),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {add_regulator(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        new_reg = Regulator(vals['name'], vals['algorithm'], vals['description'])
        real_reg = regulator_factory(new_reg.algorithm_name)
        real_reg.initialize_db(new_reg)
        DBSession.add(new_reg)
        DBSession.flush()
        ret_dict['form'] = form.render()
        ret_dict['regulator_panel'] = self.request.layout_manager.render_panel('regulator_panel', context=new_reg)
        self.request.redis.publish('regulator_changes', 'added '+str(new_reg.id))
        return ret_dict

    @view_config(route_name='regulator_update', renderer='json')
    def regulator_update(self):
        ret_dict = {}
        controls = self.request.POST.items()
        reg_id = self.request.matchdict['reg_id']
        reg = DBSession.query(Regulator).filter_by(_id=reg_id).one()
        form = Form(EditRegulatorSchema().bind(regulator=reg),
                    formid='edit_regulator_form_' + reg_id,
                    action=self.request.route_url('regulator_update', reg_id=reg_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_regulator(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['error'] = True
            ret_dict['regulator'] = reg.serialize
            ret_dict['form'] = e.render()
            return ret_dict
        reg.algorithm_name = vals['algorithm']
        real_reg = regulator_factory(reg.algorithm_name)
        real_reg.initialize_db(reg)
        DBSession.flush()
        ret_dict['form'] = form.render(regulator=reg)
        ret_dict['regulator'] = reg.serialize
        ret_dict['regulator_panel'] = self.request.layout_manager.render_panel('regulator_panel', context=reg)
        self.request.redis.publish('regulator_changes', 'changed '+str(reg.id))
        return ret_dict

    @view_config(route_name='regulator_delete', renderer='json')
    def regulator_delete(self):
        regulator = DBSession.query(Regulator).filter_by(_id=self.request.matchdict['reg_id']).first()
        DBSession.delete(regulator)
        return {'delete': True}

    @view_config(route_name='component_property_update', renderer='json')
    def component_property_update(self):
        ret_dict = {}
        prop_id = self.request.matchdict['comp_prop_id']
        ret_dict['component_property_id'] = prop_id
        controls = self.request.POST.items()
        prop = DBSession.query(ComponentProperty).filter_by(_id=prop_id).one()
        form = Form(ComponentPropertySchema().bind(),
                    formid='edit_component_property_' + prop_id,
                    action=self.request.route_url('component_property_update', comp_prop_id=prop_id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) {edit_component_property(rText);}}',
                    buttons=('Save',))
        try:
            vals = form.validate(controls)
            ret_dict['form'] = form.render()
            ret_dict['error'] = False
        except ValidationFailure as e:
            ret_dict['form'] = e.render()
            ret_dict['error'] = True
            return ret_dict
        prop.value = vals['value']
        ret_dict['component_property'] = prop.serialize
        self.request.redis.publish('component_property_changes', str(prop.id))
        return ret_dict