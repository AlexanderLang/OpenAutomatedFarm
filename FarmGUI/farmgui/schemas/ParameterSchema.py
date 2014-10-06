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
        choises.append((p.id, p.name + ' [' + p.unit + ']'))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_type_default(node, kw):
    if 'parameter' in kw:
        return kw['parameter'].parameter_type_id
    parameter_type = DBSession.query(ParameterType).first()
    return parameter_type.id


@colander.deferred
def deferred_sensor_widget(node, kw):
    sensors = DBSession.query(Sensor).all()
    choises = [(None, '--select--')]
    for s in sensors:
        choises.append((s.id, s.periphery_controller.name + '->' + s.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_sensor_default(node, kw):
    if 'parameter' in kw:
        sid = kw['parameter'].sensor_id
        if sid is None:
            return colander.null
        return sid
    return colander.null


@colander.deferred
def deferred_name_default(node, kw):
    if 'parameter' in kw:
        name = kw['parameter'].name
        if name is None:
            return colander.null
        return name
    return colander.null


@colander.deferred
def deferred_description_default(node, kw):
    if 'parameter' in kw:
        desc = kw['parameter'].description
        if desc is None:
            return colander.null
        return desc
    return colander.null


class ParameterSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Parameter Name',
                      default=deferred_name_default)
    parameter_type = SchemaNode(typ=Int(),
                                title='Parameter Type',
                                descripition='the type of physical quantity that is being measured',
                                default=deferred_type_default,
                                widget=deferred_type_widget)
    sensor = SchemaNode(typ=Int(),
                        title='Associated Sensor',
                        default=deferred_sensor_default,
                        widget=deferred_sensor_widget,
                        missing=None)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             missing=None)