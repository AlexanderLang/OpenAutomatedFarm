"""
Created on Feb 25, 2014

@author: alex
"""
from deform import Form
from ..schemas import InterpolationKnotSchema
from ..schemas import SetpointInterpolationSchema

from pyramid_layout.panel import panel_config


@panel_config(name='calendar_param_entry', renderer='farmgui:panels/templates/calendar_entry.pt')
def calendar_param_entry(context, request):
    """

    """
    return {'entry': context,
            'delete_href': request.route_url('calendar_param_entry_delete',
                                             param_id=request.matchdict['param_id'],
                                             entry_id=context.id)}


@panel_config(name='calendar_dev_entry', renderer='farmgui:panels/templates/calendar_entry.pt')
def calendar_dev_entry(context, request):
    """

    """
    return {'entry': context,
            'delete_href': request.route_url('calendar_dev_entry_delete',
                                             dev_id=request.matchdict['dev_id'],
                                             entry_id=context.id)}


@panel_config(name='setpoint_interpolation', renderer='farmgui:panels/templates/setpoint_interpolation.pt')
def setpoint_interpolation(context, request):
    """

    """
    interpolation_schema = SetpointInterpolationSchema().bind(interpolation=context)
    edit_form = Form(interpolation_schema,
                     action=request.route_url('interpolation_update', inter_id=context.id),
                     buttons=('Save',))
    knot_schema = InterpolationKnotSchema().bind()
    add_knot_form = Form(knot_schema,
                         formid='add_interpolation_knot_form_'+str(context.id),
                         action=request.route_url('interpolation_knot_save', inter_id=context.id),
                         use_ajax=True,
                         ajax_options='{"success": function(rt, st, xhr, form) {add_interpolation_knot(rt);}}',
                         buttons=('Save',))
    plot_dir = request.registry.settings['plot_directory']
    plot_href = request.static_url(plot_dir + '/interpolation_' + str(context.id) + '.png')
    return {'interpolation': context,
            'delete_href': request.route_url('interpolation_delete', inter_id=context.id),
            'plot_href': plot_href,
            'add_knot_form': add_knot_form.render(),
            'edit_form': edit_form}


@panel_config(name='interpolation_knot', renderer='farmgui:panels/templates/interpolation_knot.pt')
def interpolation_knot(context, request):
    schema = InterpolationKnotSchema().bind(knot=context)
    edit_form = Form(schema,
                     action=request.route_url('interpolation_knot_update',
                                              inter_id=context.interpolation_id,
                                              knot_id=context.id))
    return {'knot': context,
            'delete_href': request.route_url('interpolation_knot_delete',
                                             inter_id=context.interpolation_id,
                                             knot_id=context.id),
            'edit_form': edit_form}