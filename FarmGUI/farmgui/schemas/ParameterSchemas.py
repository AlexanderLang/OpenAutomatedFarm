import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int

from deform.widget import SelectWidget

from farmgui.models import DBSession
from farmgui.models import Sensor
from farmgui.models import ParameterType
from farmgui.schemas import ComponentSchema


@colander.deferred
def deferred_sensor_widget(node, kw):
    query = DBSession.query(Sensor)
    if 'parameter' in kw:
        query = query.filter_by(parameter_type_id=kw['parameter'].parameter_type_id)
    sensors = query.all()
    choices = [(None, '--select--')]
    for s in sensors:
        choices.append((s.id, s.periphery_controller.name + '->' + s.name))
    return SelectWidget(values=choices)


@colander.deferred
def deferred_sensor_default(node, kw):
    if 'parameter' in kw:
        sid = kw['parameter'].sensor_id
        if sid is None:
            return colander.null
        return sid
    return colander.null


@colander.deferred
def deferred_type_widget(node, kw):
    types = DBSession.query(ParameterType).all()
    choices = [(None, '--select--')]
    for t in types:
        choices.append((t.id, t.name + ' [' + t.unit + ']'))
    return SelectWidget(values=choices)


class NewParameterSchema(ComponentSchema):
    parameter_type = SchemaNode(typ=Int(),
                            title='Parameter Type',
                            widget=deferred_type_widget)


class EditParameterSchema(MappingSchema):
    sensor = SchemaNode(typ=Int(),
                        title='Associated Sensor',
                        default=deferred_sensor_default,
                        widget=deferred_sensor_widget,
                        missing=None)