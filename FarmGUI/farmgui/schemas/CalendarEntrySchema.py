import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int

from deform.widget import SelectWidget

from farmgui.models import DBSession
from farmgui.models import SetpointInterpolation


@colander.deferred
def deferred_interpolation_widget(node, kw):
    interpolations = DBSession.query(SetpointInterpolation).all()
    choises = [(None, '--select--')]
    for ip in interpolations:
        choises.append((ip.id, ip.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_interpolation_default(node, kw):
    if len(kw) > 0:
        return kw['entry'].interpolation_id
    return 0


class CalendarEntrySchema(MappingSchema):
    interpolation = SchemaNode(typ=Int(),
                                title='Interpolation',
                                descripition='the type of device being controlled',
                                default=deferred_interpolation_default,
                                widget=deferred_interpolation_widget)