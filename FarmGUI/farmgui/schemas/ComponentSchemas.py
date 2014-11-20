import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import Int

from deform.widget import SelectWidget
from deform.widget import TextInputWidget

from farmgui.models import DBSession
from farmgui.models import ComponentOutput
from farmgui.models import ComponentProperty


@colander.deferred
def deferred_name_default(node, kw):
    if 'component' in kw:
        name = kw['component'].name
        if name is None:
            return colander.null
        return name
    elif 'component_property' in kw:
        return kw['component_property'].name
    return colander.null


@colander.deferred
def deferred_description_default(node, kw):
    if 'component' in kw:
        desc = kw['component'].description
        if desc is None:
            return colander.null
        return desc
    return colander.null


@colander.deferred
def deferred_connected_output_widget(node, kw):
    query = DBSession.query(ComponentOutput)
    if 'device' in kw:
        query = query.filter_by(device_type_id=kw['device'].device_type_id)
    outputs = query.all()
    choices = [(None, '--select--')]
    for outp in outputs:
        choices.append((outp.id, outp.component.name + '->' + outp.name))
    return SelectWidget(values=choices)


@colander.deferred
def deferred_connected_output_default(node, kw):
    if len(kw) > 0:
        if 'device' in kw.keys():
            aid = kw['device'].actuator_id
            if aid is None:
                return colander.null
            return aid
        elif 'component_input' in kw.keys():
            con_id = kw['component_input'].connected_output_id
            if con_id is None:
                return colander.null
            return con_id
    return colander.null


@colander.deferred
def deferred_value_default(node, kw):
    if len(kw) > 0:
        return kw['component_property'].value
    fs = DBSession.query(ComponentProperty).first()
    return fs.value


@colander.deferred
def deferred_title_default(node, kw):
    if len(kw) > 0:
        return kw['component_property'].name
    return 'no_name'


class ComponentPropertySchema(MappingSchema):
    value = SchemaNode(typ=String(),
                       title=deferred_title_default,
                       default=deferred_value_default,
                       widget=TextInputWidget())


class ComponentInputSchema(MappingSchema):
    connected_output = SchemaNode(typ=Int(),
                                  title='Connect to',
                                  default=deferred_connected_output_default,
                                  widget=deferred_connected_output_widget,
                                  missing=None)


class ComponentSchema(MappingSchema):
    name = SchemaNode(typ=String(),
                      title='Name',
                      default=deferred_name_default)
    description = SchemaNode(typ=String(),
                             title='Description',
                             default=deferred_description_default,
                             missing=None)
