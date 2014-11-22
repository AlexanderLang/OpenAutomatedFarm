import colander
from colander import SchemaNode
from colander import String

from farmgui.schemas import DisplaySchema


@colander.deferred
def deferred_period_default(node, kw):
    if 'log_diagram' in kw:
        period = kw['log_diagram'].period
        if period is None:
            return colander.null
        return period
    return colander.null


class LogDiagramSchema(DisplaySchema):
    period = SchemaNode(typ=String(),
                        title='Period',
                      default=deferred_period_default)