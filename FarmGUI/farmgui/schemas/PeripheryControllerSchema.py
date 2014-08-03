import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import TextInputWidget


@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        return kw['periphery_controller'].name
    return colander.null


class PeripheryControllerSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Name',
                      default=deferred_name_default,
                      widget=TextInputWidget(size=40))