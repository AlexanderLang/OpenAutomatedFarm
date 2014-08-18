import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import TextInputWidget


@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        return kw['component'].name
    return ''

@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        return kw['component'].description
    return ''



class FarmComponentSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Component Name',
                      default=deferred_name_default,
                      widget=TextInputWidget(size=40))
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             widget=TextInputWidget(size=80),
                             missing=None)