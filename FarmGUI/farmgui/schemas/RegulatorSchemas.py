import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String

from deform.widget import SelectWidget

from farmgui.regulators import get_regulator_list
from farmgui.schemas import ComponentSchema


@colander.deferred
def deferred_algorithm_default(node, kw):
    if len(kw) > 0:
        algo = kw['regulator'].algorithm_name
        if algo is None:
            return colander.null
        return algo
    return colander.null


@colander.deferred
def deferred_algorithm_widget(node, kw):
    choices = []
    for name in get_regulator_list():
        choices.append((name, name))
    return SelectWidget(values=choices)


class NewRegulatorSchema(ComponentSchema):
    algorithm = SchemaNode(typ=String(),
                           title='Algorithm',
                           descripition='control algorithm name',
                           default=deferred_algorithm_default,
                           widget=deferred_algorithm_widget)


class EditRegulatorSchema(MappingSchema):
    algorithm = SchemaNode(typ=String(),
                           title='Algorithm',
                           descripition='control algorithm name',
                           default=deferred_algorithm_default,
                           widget=deferred_algorithm_widget)