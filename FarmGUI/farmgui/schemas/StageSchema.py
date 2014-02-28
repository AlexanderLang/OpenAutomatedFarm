
from colander import MappingSchema
from colander import SchemaNode
from colander import Int
from colander import String

class StageSchema(MappingSchema):
    Number = SchemaNode(Int())
    Duration = SchemaNode(Int())
    Name = SchemaNode(String(), missing=None)
    Description = SchemaNode(String(), missing=None)