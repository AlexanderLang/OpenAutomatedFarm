
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import Float
from colander import String

class ParameterSchema(MappingSchema):
    Name = SchemaNode(String())
    Unit = SchemaNode(String())
    Minimum = SchemaNode(Float())
    Maximum = SchemaNode(Float())
    Description = SchemaNode(String(), missing=None)