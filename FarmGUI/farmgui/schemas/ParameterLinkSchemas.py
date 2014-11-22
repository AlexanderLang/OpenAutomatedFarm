import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import String
from deform.widget import SelectWidget

from farmgui.models import DBSession
from farmgui.models import Parameter


@colander.deferred
def deferred_parameter_widget(node, kw):
    parameters = DBSession.query(Parameter).all()
    choices = [(None, '--select--')]
    for s in parameters:
        choices.append((s.id, s.name))
    return SelectWidget(values=choices)


@colander.deferred
def deferred_parameter_default(node, kw):
    if 'parameter_link' in kw:
        sid = kw['parameter_link'].parameter_id
        if sid is None:
            return colander.null
        return sid
    return colander.null


class ParameterLinkSchema(MappingSchema):
    parameter = SchemaNode(typ=Int(),
                         title='Parameter',
                         default=deferred_parameter_default,
                         widget=deferred_parameter_widget)
    target = SchemaNode(typ=String(),
                             title='Target Log',
                             default='value',
                             widget=SelectWidget(values=[('value', 'Values'), ('setpoint', 'Setpoints')]))