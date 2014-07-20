
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import Time
from colander import Float

from deform.widget import SelectWidget

from ..models import DBSession
from ..models import Parameter

from datetime import time

class StageConfigurationSchema(MappingSchema):
    parameter = SchemaNode(
                           typ = Int(),
                           title = 'Parameter',
                           widget = SelectWidget(values=[
                                                         (_id, name) for _id, name in 
                                                         DBSession.query(Parameter._id, Parameter.name)]))
    time = SchemaNode(
                      typ = Time(),
                      title = 'Time',
                      default = time(0, 0))
    setpoint = SchemaNode(
                          typ = Float(),
                          title = 'Setpoint')
    upper_limit = SchemaNode(typ = Float(),
                            title = 'Upper limit')
    lower_limit = SchemaNode(typ = Float(),
                            title = 'Lower limit')