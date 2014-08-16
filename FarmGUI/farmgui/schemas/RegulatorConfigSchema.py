import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import TextInputWidget

from ..models import DBSession
from ..models import RegulatorConfig

@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        return kw['config'].name
    rc = DBSession.query(RegulatorConfig).first()
    return rc.name

@colander.deferred
def deferred_value_default(node, kw):
    if len(kw) > 0:
        return kw['config'].value
    rc = DBSession.query(RegulatorConfig).first()
    return rc.value

@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        return kw['config'].description
    rc = DBSession.query(RegulatorConfig).first()
    return rc.description


class RegulatorConfigSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Name',
                      default=deferred_name_default,
                      widget=TextInputWidget(readonly=True))
    value = SchemaNode(typ=String(),
                       title='Value',
                       default=deferred_value_default,
                       widget=TextInputWidget())
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             widget=TextInputWidget(readonly=True),
                             missing=None)