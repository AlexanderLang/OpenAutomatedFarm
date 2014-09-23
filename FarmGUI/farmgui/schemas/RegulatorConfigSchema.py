import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import TextInputWidget

from ..models import DBSession
from ..models import RegulatorConfig

@colander.deferred
def deferred_value_default(node, kw):
    if len(kw) > 0:
        return kw['config'].value
    rc = DBSession.query(RegulatorConfig).first()
    return rc.value


class RegulatorConfigSchema(MappingSchema):
    value = SchemaNode(typ=String(),
                       title='Value',
                       default=deferred_value_default,
                       widget=TextInputWidget())