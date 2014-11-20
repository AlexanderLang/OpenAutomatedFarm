"""
Created on Jul 20, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from farmgui.schemas import ComponentSchema
from farmgui.schemas import EditParameterSchema
from farmgui.schemas import EditDeviceSchema
from farmgui.schemas import EditRegulatorSchema
from farmgui.schemas import ComponentInputSchema
from farmgui.schemas import ComponentPropertySchema


@panel_config(name='component_panel',
              context='farmgui.models.Component',
              renderer='farmgui:panels/templates/component_panel.pt')
def component_panel(context, request):
    schema = ComponentSchema().bind(component=context)
    edit_component_form = Form(schema,
                               action=request.route_url('component_update', comp_id=context.id),
                               formid='edit_component_form_' + str(context.id),
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            '  edit_component(rText);}}',
                               buttons=('Save',))
    return {'component': context,
            'edit_component_form': edit_component_form.render(),
            'delete_href': request.route_url('component_delete', comp_id=context.id)}


@panel_config(name='parameter_panel',
              context='farmgui.models.Parameter',
              renderer='farmgui:panels/templates/parameter_panel.pt')
def parameter_panel(context, request):
    schema = EditParameterSchema().bind(parameter=context)
    edit_parameter_form = Form(schema,
                               action=request.route_url('parameter_update', param_id=context.id),
                               formid='edit_parameter_form_' + str(context.id),
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            '  edit_parameter(rText);}}',
                               buttons=('Save',))
    sensor_name = 'No sensor selected'
    if context.sensor is not None:
        sensor_name = context.sensor.periphery_controller.name + '-->' + context.sensor.name
    return {'parameter': context,
            'sensor_name': sensor_name,
            'edit_parameter_form': edit_parameter_form.render(),
            'delete_href': request.route_url('parameter_delete', param_id=context.id),
            'calendar_href': request.route_url('calendar_home', parameter_id=context.id)}


@panel_config(name='device_panel',
              context='farmgui.models.Device',
              renderer='farmgui:panels/templates/device_panel.pt')
def device_panel(context, request):
    schema = EditDeviceSchema().bind(device=context)
    edit_device_form = Form(schema,
                            action=request.route_url('device_update', dev_id=context.id),
                            formid='edit_device_form_' + str(context.id),
                            use_ajax=True,
                            ajax_options='{"success": function (rText, sText, xhr, form) {'
                                         '  edit_device(rText);}}',
                            buttons=('Save',))
    actuator_name = 'No actuator selected'
    if context.actuator is not None:
        actuator_name = context.actuator.periphery_controller.name + '-->' + context.actuator.name
    return {'device': context,
            'actuator_name': actuator_name,
            'edit_device_form': edit_device_form.render(),
            'delete_href': request.route_url('device_delete', dev_id=context.id)}


@panel_config(name='regulator_panel',
              context='farmgui.models.Regulator',
              renderer='farmgui:panels/templates/regulator_panel.pt')
def regulator_panel(context, request):
    schema = EditRegulatorSchema().bind(regulator=context)
    edit_regulator_form = Form(schema,
                               action=request.route_url('regulator_update', reg_id=context.id),
                               formid='edit_regulator_form_' + str(context.id),
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            '  edit_regulator(rText);}}',
                               buttons=('Save',))
    return {'regulator': context,
            'edit_regulator_form': edit_regulator_form.render(),
            'delete_href': request.route_url('regulator_delete', reg_id=context.id)}


@panel_config(name='component_property_panel', renderer='farmgui:panels/templates/component_property_panel.pt')
def component_property_panel(context, request):
    schema = ComponentPropertySchema().bind(component_property=context)
    edit_form = Form(schema,
                     action=request.route_url('component_property_update', comp_prop_id=context.id),
                     formid='edit_component_property_form_' + str(context.id),
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) {edit_component_property(rText);}}',
                     buttons=('Save',))
    print('\n\n'+edit_form.render({'name': context.name, 'value': context.value}))
    return {'component_property': context,
            'edit_form': edit_form.render()}


@panel_config(name='component_output_panel',
              context='farmgui.models.ComponentOutput',
              renderer='farmgui:panels/templates/component_output_panel.pt')
def component_output_panel(context, request):
    return {'component_output': context}


@panel_config(name='component_input_panel',
              context='farmgui.models.ComponentInput',
              renderer='farmgui:panels/templates/component_input_panel.pt')
def component_input_panel(context, request):
    schema = ComponentInputSchema().bind(component_input=context)
    edit_form = Form(schema,
                               action=request.route_url('component_input_update', comp_in_id=context.id),
                               formid='edit_component_input_form_' + str(context.id),
                               use_ajax=True,
                               ajax_options='{"success": function (rText, sText, xhr, form) {'
                                            '  edit_component_input(rText);}}',
                               buttons=('Save',))
    connected_output_name = 'not connected'
    if context.connected_output is not None:
        connected_output_name = context.connected_output.component.name + ': ' + context.connected_output.name
    return {'component_input': context,
            'connected_output_name': connected_output_name,
            'edit_component_input_form': edit_form.render()}

