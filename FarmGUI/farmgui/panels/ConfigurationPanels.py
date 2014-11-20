"""
Created on Jul 20, 2014

@author: alex
"""

from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from ..models import DBSession
from ..models import PeripheryController
from ..models import FieldSetting
from ..models import Sensor
from ..models import Actuator

from ..schemas import FieldSettingSchema
from ..schemas import PeripheryControllerSchema


@panel_config(name='field_setting_panel', renderer='farmgui:panels/templates/field_setting_panel.pt')
def field_setting_panel(context, request, field_setting_name):
    field_setting = DBSession.query(FieldSetting).filter_by(name=field_setting_name).one()
    schema = FieldSettingSchema(field_setting=field_setting).bind()
    edit_form = Form(schema,
                     action=request.route_url('setting_views_update', name=field_setting_name),
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

