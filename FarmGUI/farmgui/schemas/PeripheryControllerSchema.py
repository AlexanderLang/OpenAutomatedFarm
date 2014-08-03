import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String


@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        return kw['periphery_controller'].name
    return colander.null


class PeripheryControllerSchema(MappingSchema):
    Name = SchemaNode(typ=String(),
                      title='Description',
                      default=deferred_name_default)