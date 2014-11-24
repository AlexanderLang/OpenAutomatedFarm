import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import String
from deform.widget import SelectWidget
from deform.widget import TextInputWidget

from farmgui.models import DBSession
from farmgui.models import Device


@colander.deferred
def deferred_device_widget(node, kw):
    devices = DBSession.query(Device).all()
    choices = [(None, '--select--')]
    for d in devices:
        choices.append((d.id, d.name))
    return SelectWidget(values=choices)


@colander.deferred
def deferred_device_default(node, kw):
    if 'device_link' in kw:
        sid = kw['device_link'].device_id
        if sid is None:
            return colander.null
        return sid
    return colander.null


class DeviceLinkSchema(MappingSchema):
    device = SchemaNode(typ=Int(),
                        title='Parameter',
                        default=deferred_device_default,
                        widget=deferred_device_widget)
    target = SchemaNode(typ=String(),
                        title='Target Log',
                        default='value',
                        widget=SelectWidget(values=[('value', 'Values'), ('setpoint', 'Setpoints')]))
    color = SchemaNode(typ=String(),
                       title='Color',
                       default='#FF0000',
                       widget=TextInputWidget())