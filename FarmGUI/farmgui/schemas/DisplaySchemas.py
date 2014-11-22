import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String


@colander.deferred
def deferred_name_default(node, kw):
    if 'log_diagram' in kw:
        name = kw['log_diagram'].name
        if name is None:
            return colander.null
        return name
    return colander.null


@colander.deferred
def deferred_description_default(node, kw):
    if 'log_diagram' in kw:
        desc = kw['log_diagram'].description
        if desc is None:
            return colander.null
        return desc
    return colander.null


class DisplaySchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Name',
                      default=deferred_name_default)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             missing=None)
