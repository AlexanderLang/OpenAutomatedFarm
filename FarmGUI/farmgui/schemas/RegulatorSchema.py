import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import Float
from colander import String
from colander import Range

from deform.widget import SelectWidget
from deform.widget import TextInputWidget
from deform.widget import HiddenWidget

from ..models import DBSession
from ..models import Parameter
from ..models import RegulatorType
from ..models import Device


@colander.deferred
def deferred_type_widget(node, kw):
    dev_types = DBSession.query(RegulatorType).all()
    choises = []
    for rt in dev_types:
        choises.append((rt.id, rt.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_type_default(node, kw):
    if len(kw) > 0:
        return kw['regulator'].regulator_type_id
    regulator_type = DBSession.query(RegulatorType).first()
    return regulator_type.id


@colander.deferred
def deferred_parameter_widget(node, kw):
    parameters = DBSession.query(Parameter).all()
    choises = [(None, '--select--')]
    for p in parameters:
        choises.append((p.id, p.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_parameter_default(node, kw):
    if len(kw) > 0:
        aid = kw['regulator'].input_parameter_id
        if aid is None:
            return colander.null
        return aid
    return colander.null


@colander.deferred
def deferred_device_widget(node, kw):
    devices = DBSession.query(Device).all()
    choises = [(None, '--select--')]
    for d in devices:
        choises.append((d.id, d.name))
    return SelectWidget(values=choises)


@colander.deferred
def deferred_device_default(node, kw):
    if len(kw) > 0:
        aid = kw['regulator'].output_device_id
        if aid is None:
            return colander.null
        return aid
    return colander.null


@colander.deferred
def deferred_name_default(node, kw):
    if len(kw) > 0:
        name = kw['regulator'].name
        if name is None:
            return colander.null
        return name
    return colander.null


@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        desc = kw['regulator'].description
        if desc is None:
            return colander.null
        return desc
    return colander.null


class RegulatorSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Regulator Name',
                      default=deferred_name_default)
    regulator_type = SchemaNode(typ=Int(),
                                title='Regulator Type',
                                descripition='the type of device being controlled',
                                default=deferred_type_default,
                                widget=deferred_type_widget)
    parameter = SchemaNode(typ=Int(),
                        title='Input Pameter',
                        default=deferred_parameter_default,
                        widget=deferred_parameter_widget,)
    device = SchemaNode(typ=Int(),
                        title='Output Device',
                        default=deferred_device_default,
                        widget=deferred_device_widget)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             widget=TextInputWidget(),
                             missing=None)