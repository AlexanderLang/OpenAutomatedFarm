
import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import Float
from colander import String
from colander import Range

from deform.widget import SelectWidget
from deform.widget import TextInputWidget
from deform.widget import HiddenWidget

from ..models import DBSession
from ..models import Sensor
from ..models import ParameterType


@colander.deferred
def deferred_type_widget(node, kw):
    parameters = DBSession.query(ParameterType).all()
    choises = []
    for p in parameters:
        choises.append((p._id, p.name + ' [' + p.unit + ']'))
    return SelectWidget(values=choises)

@colander.deferred
def deferred_type_default(node, kw):
    if len(kw) > 0:
        return kw['parameter'].parameter_type_id
    parameter_type = DBSession.query(ParameterType).first()
    return parameter_type._id

@colander.deferred
def deferred_interval_default(node, kw):
    if len(kw) > 0:
        return kw['parameter'].interval
    return 15

@colander.deferred
def deferred_sensor_widget(node, kw):
    sensors = DBSession.query(Sensor).all()
    choises = []
    for s in sensors:
        choises.append((s._id, s.periphery_controller.name+'->'+s.name))
    return SelectWidget(values=choises)

class ParameterSchema(MappingSchema):
    component = SchemaNode(typ=Int(),
                           title='Farm Component',
                           description='component the parameter belongs to',
                           widget=HiddenWidget(readonly=True))
    name = SchemaNode(String())
    parameter_type = SchemaNode(typ=Int(),
                      title='Parameter Type',
                      descripition='the type of physical quantity that is being measured',
                      default=deferred_type_default,
                      widget=deferred_type_widget)
    interval = SchemaNode(typ=Float(),
                          title='Measurement interval [s]',
                          validation=Range(0, 10),
                          default=deferred_interval_default,
                          widget=TextInputWidget())
    sensor = SchemaNode(typ=Int(),
                        title='Sensor',
                        widget=deferred_sensor_widget,
                        missing=None)
    description = SchemaNode(String(), missing=None)