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
    value = SchemaNode(typ=String(),
                       title=deferred_name_default,
                       default=deferred_value_default,
                       description=deferred_description_default,
                       widget=TextInputWidget())