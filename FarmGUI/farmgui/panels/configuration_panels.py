'''
Created on Jul 20, 2014

@author: alex
'''


from pyramid_layout.panel import panel_config
from deform_bootstrap import Form

from ..models import DBSession
from ..models import FarmComponent
from ..models import Parameter

from ..schemas import ParameterSchema
from colanderalchemy import SQLAlchemySchemaNode

@panel_config(name='component_panel', renderer='farmgui:panels/templates/component_panel.pt')
def component_panel(context, request, component_id):
    component = DBSession.query(FarmComponent).filter(FarmComponent._id == component_id).first()
    schema = ParameterSchema(component=component).bind()
    add_parameter_form = Form(schema, action=request.route_url('parameter_save'), formid='addParameterForm_'+str(component_id), buttons=('Save',))
    return {'component': component,
            'add_parameter_form': add_parameter_form.render({'component': component._id}),
            'delete_href': request.route_url('component_delete', _id=component._id)
            }

@panel_config(name='parameter_panel', renderer='farmgui:panels/templates/parameter_panel.pt')
def parameter_panel(context, request, parameter_id):
    parameter = DBSession.query(Parameter).filter(Parameter._id == parameter_id).first()
    return {'parameter': parameter,
            'delete_href': request.route_url('parameter_delete', _id=parameter._id)
            }

