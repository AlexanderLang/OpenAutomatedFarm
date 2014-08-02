from colander import MappingSchema
from colander import SchemaNode
from colander import String


class FarmComponentSchema(MappingSchema):
    Name = SchemaNode(String())
    Description = SchemaNode(String(), missing=None)