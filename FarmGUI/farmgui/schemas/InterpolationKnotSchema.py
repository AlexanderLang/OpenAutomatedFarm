import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import Float
from deform.widget import HiddenWidget


@colander.deferred
def deferred_interpolation_id_default(node, kw):
    if len(kw) > 0:
        return kw['knot'].interpolation_id
    return 0


@colander.deferred
def deferred_time_default(node, kw):
    if len(kw) > 0:
        return kw['knot'].time
    return 0


@colander.deferred
def deferred_value_default(node, kw):
    if len(kw) > 0:
        return kw['knot'].value
    return 0


class InterpolationKnotSchema(MappingSchema):
    interpolation_id = SchemaNode(typ=Int(),
                                  title='Name',
                                  default=deferred_interpolation_id_default,
                                  widget=HiddenWidget(readonly=True))
    time = SchemaNode(typ=Float(),
                      title='Time',
                      description='between 0 and 1 (becomes start to end time)',
                      default=deferred_time_default)
    value = SchemaNode(typ=Float(),
                       title='Value',
                       default=deferred_value_default)