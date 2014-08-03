"""
Created on Jul 20, 2014

@author: alex
"""

import colander

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from ..models import DBSession
from ..models import FarmComponent
from ..models import Parameter
from ..models import FieldSetting

from ..schemas import ParameterSchema
from ..schemas import FieldSettingSchema

@panel_config(name='component_panel', renderer='farmgui:panels/templates/component_panel.pt')
def component_panel(context, request, component_id):
    """

    :type component_id: int
    """
    component = DBSession.query(FarmComponent).filter_by(_id=component_id).first()
    schema = ParameterSchema(component=component).bind()
    add_parameter_form = Form(schema,
                              action=request.route_url('parameter_save'),
                              formid='addParameterForm_' + str(component_id),
                              buttons=('Save',))
    return {'component': component,
            'add_parameter_form': add_parameter_form.render({'component': component.id}),
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
            'delete_href': request.route_url('parameter_delete', _id=parameter.id)}


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

