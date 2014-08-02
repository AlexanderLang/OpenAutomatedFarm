from colander import MappingSchema
from colander import SchemaNode
from colander import String


class PlantSettingsSchema(MappingSchema):
    Plant = SchemaNode(String())
    Variety = SchemaNode(String())
    Method = SchemaNode(String())
    Description = SchemaNode(String(), missing=None)