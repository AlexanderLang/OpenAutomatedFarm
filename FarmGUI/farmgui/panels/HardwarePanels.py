"""
Created on Jul 20, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from farmgui.schemas import PeripheryControllerSchema


@panel_config(name='periphery_controller_panel', renderer='farmgui:panels/templates/periphery_controller_panel.pt')
def periphery_controller_panel(context, request):
    schema = PeripheryControllerSchema().bind(periphery_controller=context)
    edit_periphery_controller_form = Form(schema,
                     action=request.route_url('periphery_controller_update', pc_id=context.id),
                     formid='edit_periphery_controller_form_'+str(context.id),
                    use_ajax=True,
                    ajax_options='{"success": function (rText, sText, xhr, form) { edit_periphery_controller(rText);}}',
                     buttons=('Save',))
    return {'periphery_controller': context,
            'delete_href': request.route_url('periphery_controller_delete', pc_id=context.id),
            'edit_periphery_controller_form': edit_periphery_controller_form.render()}


@panel_config(name='sensor_panel', renderer='farmgui:panels/templates/sensor_panel.pt')
def sensor_panel(context, request):
    return {'sensor': context}


@panel_config(name='actuator_panel', renderer='farmgui:panels/templates/actuator_panel.pt')
def actuator_panel(context, request):
    return {'actuator': context}

