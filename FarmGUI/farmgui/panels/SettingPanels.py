"""
Created on Jul 20, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from farmgui.models import DBSession
from farmgui.models import FieldSetting

from farmgui.schemas import FieldSettingSchema


@panel_config(name='field_setting_panel', renderer='farmgui:panels/templates/field_setting_panel.pt')
def field_setting_panel(context, request):
    schema = FieldSettingSchema().bind(field_setting=context)
    edit_form = Form(schema,
                     action=request.route_url('field_setting_update', name=context.name),
                     formid='edit_field_setting_form_'+context.name,
                     use_ajax=True,
                     ajax_options='{"success": function (rText, sText, xhr, form) { edit_field_setting(rText);}}',
                     buttons=('Save',))
    return {'field_setting': context,
            'edit_form': edit_form.render()}
