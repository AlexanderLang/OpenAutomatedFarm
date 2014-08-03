import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import TextInputWidget

from ..models import DBSession
from ..models import FieldSetting

@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        return kw['field_setting'].name
    fs = DBSession.query(FieldSetting).first()
    return fs.name

@colander.deferred
def deferred_value_default(node, kw):
    if len(kw) > 0:
        return kw['field_setting'].value
    fs = DBSession.query(FieldSetting).first()
    return fs.value

@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        return kw['field_setting'].description
    fs = DBSession.query(FieldSetting).first()
    return fs.description


class FieldSettingSchema(MappingSchema):
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