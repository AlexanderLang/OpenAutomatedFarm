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
from ..models import Actuator
from ..models import DeviceType


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
    actuators = DBSession.query(Actuator).all()
    choises = [(None, '--select--')]
    for a in actuators:
        choises.append((a.id, a.periphery_controller.name + '->' + a.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_actuator_default(node, kw):
    if len(kw) > 0:
        aid = kw['device'].actuator_id
        if aid is None:
            return colander.null
        return aid
    return colander.null


@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        name = kw['device'].name
        if name is None:
            return colander.null
        return name
    return colander.null


@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        desc = kw['device'].description
        if desc is None:
            return colander.null
        return desc
    return colander.null


class DeviceSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Device Name',
                      default=deferred_name_default)
    device_type = SchemaNode(typ=Int(),
                                title='Device Type',
                                descripition='the type of device being controlled',
                                default=deferred_type_default,
                                widget=deferred_type_widget)
    actuator = SchemaNode(typ=Int(),
                        title='Associated Actuator',
                        default=deferred_actuator_default,
                        widget=deferred_actuator_widget,
                        missing=None)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             widget=TextInputWidget(),
                             missing=None)