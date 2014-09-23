"""
Created on Jul 20, 2014

@author: alex
"""

import colander

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from ..models import DBSession
from ..models import PeripheryController
from ..models import FarmComponent
from ..models import Parameter
from ..models import FieldSetting
from ..models import Sensor
from ..models import Actuator
from ..models import Device
from ..models import Regulator

from ..schemas import FarmComponentSchema
from ..schemas import ParameterSchema
from ..schemas import DeviceSchema
from ..schemas import FieldSettingSchema
from ..schemas import PeripheryControllerSchema
from ..schemas import RegulatorSchema
from ..schemas import RegulatorConfigSchema

@panel_config(name='component_panel', renderer='farmgui:panels/templates/component_panel.pt')
def component_panel(context, request, component):
    """

    :type component_id: int
    """
    add_parameter_form = Form(ParameterSchema().bind(),
                              action=request.route_url('parameter_save', comp_id=component.id, param_id=0),
                              formid='add_parameter_form_' + str(component.id),
                              use_ajax=True,
                              ajax_options='{"success": function (rText, sText, xhr, form) {'
                                           'add_parameter(rText, sText, xhr, form);}}',
                              buttons=('Save',))
    add_device_form = Form(DeviceSchema().bind(),
                           action=request.route_url('device_save', comp_id=component.id, dev_id=0),
                           formid='add_device_form_' + str(component.id),
                           use_ajax=True,
                           ajax_options='{"success": function (rText, sText, xhr, form) {'
                                        'add_device(rText, sText, xhr, form);}}',
                           buttons=('Save',))
    add_regulator_form = Form(RegulatorSchema().bind(),
                              action=request.route_url('regulator_save', comp_id=component.id, reg_id=0),
                              formid='add_regulator_form_' + str(component.id),
                              use_ajax=True,
                              ajax_options='{"success": function (rText, sText, xhr, form) {'
                                           'add_regulator(rText, sText, xhr, form);}}',
                              buttons=('Save',))
    edit_component_form = Form(FarmComponentSchema().bind(component=component),
                               action=request.route_url('component_save', comp_id=component.id),
                               formid='edit_component_form_'+str(component.id),
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            '  edit_component(rText, sText, xhr, form);}}',
                               buttons=('Save',))
    return {'component': component,
            'edit_component_form': edit_component_form.render(),
            'add_parameter_form': add_parameter_form.render(),
            'add_device_form': add_device_form.render(),
            'add_regulator_form': add_regulator_form.render(),
            'delete_href': request.route_url('component_delete', comp_id=component.id)}


@panel_config(name='parameter_panel', renderer='farmgui:panels/templates/parameter_panel.pt')
def parameter_panel(context, request, parameter):
    schema = ParameterSchema().bind(parameter=parameter)
    edit_parameter_form = Form(schema,
                     action=request.route_url('parameter_save', comp_id=parameter.component_id, param_id=parameter.id),
                     formid='edit_parameter_form_'+str(parameter.id),
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) {'
                                  '  edit_parameter(rText, sText, xhr, form);}}',
                     buttons=('Save',))
    return {'parameter': parameter,
            'edit_parameter_form': edit_parameter_form.render(),
            'delete_href': request.route_url('parameter_delete', comp_id=parameter.component_id, param_id=parameter.id),
            'calendar_href': request.route_url('calendar_home', parameter_id=parameter.id)}


@panel_config(name='device_panel', renderer='farmgui:panels/templates/device_panel.pt')
def device_panel(context, request, device):
    schema = DeviceSchema().bind(device=device)
    edit_device_form = Form(schema,
                     action=request.route_url('device_save', comp_id=device.component_id, dev_id=device.id),
                     formid='edit_device_form_'+str(device.id),
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) {'
                                  '  edit_device(rText, sText, xhr, form);}}',
                     buttons=('Save',))
    return {'device': device,
            'edit_device_form': edit_device_form.render(),
            'delete_href': request.route_url('device_delete', comp_id=device.component_id, dev_id=device.id)}


@panel_config(name='regulator_panel', renderer='farmgui:panels/templates/regulator_panel.pt')
def regulator_panel(context, request, regulator):
    schema = RegulatorSchema().bind(regulator=regulator)
    edit_regulator_form = Form(schema,
                     action=request.route_url('regulator_save', comp_id=regulator.component_id, reg_id=regulator.id),
                     formid='edit_regulator_form_'+str(regulator.id),
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) {'
                                  '  edit_regulator(rText, sText, xhr, form);}}',
                     buttons=('Save',))
    return {'regulator': regulator,
            'edit_regulator_form': edit_regulator_form.render(),
            'delete_href': request.route_url('regulator_delete', comp_id=regulator.component_id, reg_id=regulator.id)}


@panel_config(name='regulator_config_panel', renderer='farmgui:panels/templates/regulator_config_panel.pt')
def regulator_config_panel(context, request, regulator_config):
    schema = RegulatorConfigSchema(config=regulator_config).bind()
    edit_form = Form(schema,
                     action=request.route_url('regulator_config_update', _id=regulator_config.id, reg_id=regulator_config.regulator.id),
                     formid='edit_regulator_config_form_'+str(regulator_config.id),
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) {'
                                  '  edit_regulator_config(rText, sText, xhr, form);}}',
                     buttons=('Save',))
    return {'regulator_config': regulator_config,
            'edit_form': edit_form.render({'name': regulator_config.name,
                                           'value': regulator_config.value,
                                           'description': regulator_config.description})}


@panel_config(name='field_setting_panel', renderer='farmgui:panels/templates/field_setting_panel.pt')
def field_setting_panel(context, request, field_setting_name):
    field_setting = DBSession.query(FieldSetting).filter_by(name=field_setting_name).first()
    schema = FieldSettingSchema(field_setting=field_setting).bind()
    edit_form = Form(schema,
                     action=request.route_url('field_setting_update', name=field_setting_name),
                     formid='edit_field_setting_form_'+field_setting.name,
                     buttons=('Save',))
    return {'field_setting': field_setting,
            'edit_form': edit_form.render({'name': field_setting.name,
                                           'value': field_setting.value,
                                           'description': field_setting.description})}


@panel_config(name='periphery_controller_panel', renderer='farmgui:panels/templates/periphery_controller_panel.pt')
def periphery_controller_panel(context, request, periphery_controller_id):
    periphery_controller = DBSession.query(PeripheryController).filter_by(_id=periphery_controller_id).first()
    schema = PeripheryControllerSchema().bind(periphery_controller=periphery_controller)
    edit_form = Form(schema,
                     action=request.route_url('periphery_controller_update', _id=periphery_controller_id),
                     formid='edit_periphery_controller_form_'+str(periphery_controller_id),
                     buttons=('Save',))
    return {'periphery_controller': periphery_controller,
            'delete_href': request.route_url('periphery_controller_delete', _id=periphery_controller.id),
            'edit_form': edit_form}


@panel_config(name='sensor_panel', renderer='farmgui:panels/templates/sensor_panel.pt')
def sensor_panel(context, request, sensor_id):
    sensor = DBSession.query(Sensor).filter_by(_id=sensor_id).first()
    return {'sensor': sensor}


@panel_config(name='actuator_panel', renderer='farmgui:panels/templates/actuator_panel.pt')
def actuator_panel(context, request, actuator_id):
    actuator = DBSession.query(Actuator).filter_by(_id=actuator_id).first()
    return {'actuator': actuator}

