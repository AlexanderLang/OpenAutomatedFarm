"""
Created on Feb 25, 2014

@author: alex
"""
from deform import Form
from ..schemas import InterpolationKnotSchema
from ..schemas import SetpointInterpolationSchema

from pyramid_layout.panel import panel_config


@panel_config(name='calendar_entry', renderer='farmgui:panels/templates/calendar_entry.pt')
def calendar_entry(context, request, entry):
    """

    """
    return {'entry': entry,
            'delete_href': request.route_url('calendar_entry_delete',
                                             parameter_id= request.matchdict['parameter_id'],
                                             entry_id=entry.id)}


@panel_config(name='setpoint_interpolation', renderer='farmgui:panels/templates/setpoint_interpolation.pt')
def setpoint_interpolation(context, request, interpolation):
    """

    """
    interpolation_schema = SetpointInterpolationSchema().bind(interpolation=interpolation)
    edit_form = Form(interpolation_schema,
                     action=request.route_url('interpolation_update',
                                              interpolation_id=interpolation.id,
                                              parameter_id=request.matchdict['parameter_id']),
                     buttons=('Save',))
    knot_schema = InterpolationKnotSchema().bind()
    add_knot_form = Form(knot_schema,
                                 action=request.route_url('interpolation_knot_save',
                                                          parameter_id=request.matchdict['parameter_id'],
                                                          interpolation_id=interpolation.id),
                                 formid='add_interpolation_knot_form_'+str(interpolation.id),
                                 buttons=('Save',))
    return {'interpolation': interpolation,
            'delete_href': request.route_url('interpolation_delete',
                                             parameter_id= request.matchdict['parameter_id'],
                                             interpolation_id=interpolation.id),
            'plot_href': request.static_url(request.registry.settings['plot_directory'] + '/interpolation_' + str(interpolation.id) + '.png'),
            'add_knot_form': add_knot_form.render(),
            'edit_form': edit_form}

@panel_config(name='interpolation_knot', renderer='farmgui:panels/templates/interpolation_knot.pt')
def interpolation_knot(context, request, knot):
    schema = InterpolationKnotSchema().bind(knot=knot)
    edit_form = Form(schema,
                     action=request.route_url('interpolation_knot_update',
                                              parameter_id=request.matchdict['parameter_id'],
                                              interpolation_id=knot.interpolation_id,
                                              knot_id=knot.id))
    return {'knot': knot,
            'delete_href': request.route_url('interpolation_knot_delete',
                                             parameter_id=request.matchdict['parameter_id'],
                                             interpolation_id=knot.interpolation_id,
                                             knot_id=knot.id),
            'edit_form': edit_form}