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
from ..models import SetpointInterpolation
from ..models import DeviceType


@colander.deferred
def deferred_interpolation_widget(node, kw):
    interpolations = DBSession.query(SetpointInterpolation).all()
    choises = []
    choises.append((None, '--select--'))
    for ip in interpolations:
        choises.append((ip.id, ip.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_interpolation_default(node, kw):
    if len(kw) > 0:
        return kw['entry'].interpolation_id
    return 0


@colander.deferred
def deferred_parameter_default(node, kw):
    if len(kw) > 0:
        return kw['entry'].parameter_id
    return 0


@colander.deferred
def deferred_entry_number_default(node, kw):
    if len(kw) > 0:
        return kw['entry'].entry_number
    return 0


class CalendarEntrySchema(MappingSchema):
    parameter = SchemaNode(typ=Int(),
                           title='Parameter',
                           description='parameter the entry belongs to',
                           default=deferred_parameter_default,
                           widget=HiddenWidget(readonly=True))
    entry_number = SchemaNode(typ=Int(),
                            title='Entry Number',
                            default=deferred_entry_number_default,
                            widget=HiddenWidget(readonly=True))
    interpolation = SchemaNode(typ=Int(),
                                title='Interpolation',
                                descripition='the type of device being controlled',
                                default=deferred_interpolation_default,
                                widget=deferred_interpolation_widget)