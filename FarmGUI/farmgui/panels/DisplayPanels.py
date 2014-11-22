"""
Created on Feb 25, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from farmgui.schemas import ParameterLinkSchema
from farmgui.schemas import LogDiagramSchema


@panel_config(name='log_diagram_panel', renderer='farmgui:panels/templates/log_diagram_panel.pt')
def log_diagram_panel(context, request):
    add_parameter_link_form = Form(ParameterLinkSchema().bind(),
                                   action=request.route_url('parameter_link_save', dis_id=context.id),
                                   formid='add_parameter_link_form_' + str(context.id),
                                   use_ajax=True,
                                   ajax_options='{"success": function (rText, sText, xhr, form) { add_parameter_link(rText);}}',
                                   buttons=('Save',))
    edit_log_diagram_form = Form(LogDiagramSchema().bind(log_diagram=context),
                                   action=request.route_url('log_diagram_update', ld_id=context.id),
                                   formid='edit_log_diagram_form_' + str(context.id),
                                   use_ajax=True,
                                   ajax_options='{"success": function (rText, sText, xhr, form) { edit_log_diagram(rText);}}',
                                   buttons=('Save',))
    return {'log_diagram': context,
            'add_parameter_link_form': add_parameter_link_form.render(),
            'edit_log_diagram_form': edit_log_diagram_form.render()}


@panel_config(name='parameter_link_panel', renderer='farmgui:panels/templates/parameter_link_panel.pt')
def parameter_link_panel(context, request):
    form = Form(ParameterLinkSchema().bind(parameter_link=context),
                action=request.route_url('parameter_link_update', pl_id=context.id),
                formid='edit_parameter_link_form_' + str(context.id),
                use_ajax=True,
                ajax_options='{"success": function (rText, sText, xhr, form) { edit_parameter_link(rText);}}',
                buttons=('Save',))
    return {'parameter_link': context,
            'parameter_link_name': context.parameter.name + '--&gt;' + context.target,
            'edit_parameter_link_form': form.render()}
