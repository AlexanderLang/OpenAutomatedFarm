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
from ..models import Device
from ..models import Regulator

from ..schemas import ParameterSchema
from ..schemas import DeviceSchema
from ..schemas import FieldSettingSchema
from ..schemas import PeripheryControllerSchema
from ..schemas import RegulatorSchema
from ..schemas import RegulatorConfigSchema

@panel_config(name='component_panel', renderer='farmgui:panels/templates/component_panel.pt')
def component_panel(context, request, component_id):
    """

    :type component_id: int
    """
    component = DBSession.query(FarmComponent).filter_by(_id=component_id).first()
    add_parameter_form = Form(ParameterSchema(component=component).bind(),
                              action=request.route_url('parameter_save'),
                              formid='addParameterForm_' + str(component_id),
                              buttons=('Save',))
    add_device_form = Form(DeviceSchema(component=component).bind(),
                           action=request.route_url('device_save'),
                           buttons=('Save',))
    add_regulator_form = Form(RegulatorSchema(component=component).bind(),
                              action=request.route_url('regulator_save'),
                              buttons=('Save',))
    return {'component': component,
            'add_parameter_form': add_parameter_form.render({'component': component.id}),
            'add_device_form': add_device_form.render({'component': component.id}),
            'add_regulator_form': add_regulator_form.render({'component': component.id}),
            'delete_href': request.route_url('component_delete', _id=component.id)}


@panel_config(name='parameter_panel', renderer='farmgui:panels/templates/parameter_panel.pt')
def parameter_panel(context, request, parameter_id):
    parameter = DBSession.query(Parameter).filter_by(_id=parameter_id).first()
    schema = ParameterSchema().bind(parameter=parameter)
    edit_form = Form(schema,
                     action=request.route_url('parameter_update', _id=parameter_id),
                     formid='edit_parameter_form_'+str(parameter_id),
                     buttons=('Save',))
    return {'parameter': parameter,
            'edit_form': edit_form,
            'delete_href': request.route_url('parameter_delete', _id=parameter.id),
            'calendar_href': request.route_url('calendar_home', parameter_id=parameter_id)}


@panel_config(name='device_panel', renderer='farmgui:panels/templates/device_panel.pt')
def device_panel(context, request, device_id):
    device = DBSession.query(Device).filter_by(_id=device_id).first()
    schema = DeviceSchema().bind(device=device)
    edit_form = Form(schema,
                     action=request.route_url('device_update', _id=device_id),
                     formid='edit_parameter_form_'+str(device_id),
                     buttons=('Save',))
    return {'device': device,
            'edit_form': edit_form,
            'delete_href': request.route_url('device_delete', _id=device.id)}


@panel_config(name='regulator_panel', renderer='farmgui:panels/templates/regulator_panel.pt')
def regulator_panel(context, request, regulator_id):
    regulator = DBSession.query(Regulator).filter_by(_id=regulator_id).first()
    schema = RegulatorSchema().bind(regulator=regulator)
    edit_form = Form(schema,
                     action=request.route_url('regulator_update', _id=regulator_id),
                     formid='edit_regulator_form_'+str(regulator_id),
                     buttons=('Save',))
    return {'regulator': regulator,
            'edit_form': edit_form,
            'delete_href': request.route_url('regulator_delete', _id=regulator.id)}


@panel_config(name='regulator_config_panel', renderer='farmgui:panels/templates/regulator_config_panel.pt')
def regulator_config_panel(context, request, regulator_config):
    schema = RegulatorConfigSchema(config=regulator_config).bind()
    edit_form = Form(schema,
                     action=request.route_url('regulator_config_update', _id=regulator_config.id, regulator_id=regulator_config.regulator.id),
                     formid='edit_regulator_config_form_'+str(regulator_config.id),
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
            'edit_form': edit_form}


@panel_config(name='sensor_panel', renderer='farmgui:panels/templates/sensor_panel.pt')
def sensor_panel(context, request, sensor_id):
    sensor = DBSession.query(Sensor).filter_by(_id=sensor_id).first()
    return {'sensor': sensor}

