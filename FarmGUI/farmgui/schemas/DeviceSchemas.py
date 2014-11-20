import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int

from deform.widget import SelectWidget

from farmgui.models import DBSession
from farmgui.models import Actuator
from farmgui.models import DeviceType

from farmgui.schemas import ComponentSchema


@colander.deferred
def deferred_type_widget(node, kw):
    dev_types = DBSession.query(DeviceType).all()
    choises = []
    for dt in dev_types:
        choises.append((dt.id, dt.name + ' [' + dt.unit + ']'))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_type_default(node, kw):
    if len(kw) > 0:
        return kw['device'].device_type_id
    device_type = DBSession.query(DeviceType).first()
    return device_type.id


@colander.deferred
def deferred_actuator_widget(node, kw):
    query = DBSession.query(Actuator)
    if 'device' in kw:
        query = query.filter_by(device_type_id=kw['device'].device_type_id)
    actuators = query.all()
    choices = [(None, '--select--')]
    for a in actuators:
        choices.append((a.id, a.periphery_controller.name + '->' + a.name))
    return SelectWidget(values=choices)


@colander.deferred
def deferred_actuator_default(node, kw):
    if len(kw) > 0:
        aid = kw['device'].actuator_id
        if aid is None:
            return colander.null
        return aid
    return colander.null


class NewDeviceSchema(ComponentSchema):
    device_type = SchemaNode(typ=Int(),
                                title='Device Type',
                                descripition='the type of device being controlled',
                                default=deferred_type_default,
                                widget=deferred_type_widget)


class EditDeviceSchema(MappingSchema):
    actuator = SchemaNode(typ=Int(),
                        title='Associated Actuator',
                        default=deferred_actuator_default,
                        widget=deferred_actuator_widget,
                        missing=None)