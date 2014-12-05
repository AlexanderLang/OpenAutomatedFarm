import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import Int
from colander import Float

from deform.widget import SelectWidget


@colander.deferred
def deferred_order_default(node, kw):
    if len(kw) > 0:
        return kw['interpolation'].order
    return 0


@colander.deferred
def deferred_start_value_default(node, kw):
    if len(kw) > 0:
        return kw['interpolation'].start_value
    return 0


@colander.deferred
def deferred_end_time_default(node, kw):
    if len(kw) > 0:
        return kw['interpolation'].end_time
    return 0


@colander.deferred
def deferred_end_value_default(node, kw):
    if len(kw) > 0:
        return kw['interpolation'].end_value
    return 0


@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        return kw['interpolation'].description
    return ''


class SetpointInterpolationSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Name')
    order = SchemaNode(typ=Int(),
                       title='Type (order)',
                       default=deferred_order_default,
                       widget=SelectWidget(values=[(0, 'Constant'),
                                                   (1, 'Linear'),
                                                   (2, 'Quadratic'),
                                                   (3, 'Cubic'),
                                                   (4, 'Spline')]))
    start_value = SchemaNode(typ=Float(),
                             title='Start Value',
                             default=deferred_start_value_default)
    end_time = SchemaNode(typ=Int(),
                          title='End Time',
                          default=deferred_end_time_default)
    end_value = SchemaNode(typ=Float(),
                           title='End Value',
                           default=deferred_end_value_default,
                           missing=None)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             missing=None)