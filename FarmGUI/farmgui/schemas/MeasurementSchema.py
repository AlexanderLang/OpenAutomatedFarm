
import colander
from colander import MappingSchema
from colander import SchemaNode
from colander import String
from colander import Int
from colander import Length
from colander import Float
from colander import Range

from deform.widget import SelectWidget
from deform.widget import TextInputWidget

from field_controller_database import DBSession as Field_Controller_Session
from field_controller_database import Location
from field_controller_database import Measurand
from field_controller_database import Sensor

@colander.deferred
def deferred_location_default(node, kw):
    if len(kw) > 0:
        return kw['measurement'].location._id
    location = Field_Controller_Session.query(Location).first()
    return location._id

@colander.deferred
def deferred_measurand_default(node, kw):
    if len(kw) > 0:
        return kw['measurement'].measurand._id
    measurand = Field_Controller_Session.query(Measurand).first()
    return measurand._id

@colander.deferred
def deferred_sensor_default(node, kw):
    if len(kw) > 0:
        return kw['measurement'].sensor._id
    sensor = Field_Controller_Session.query(Sensor).first()
    return sensor._id

@colander.deferred
def deferred_description_default(node, kw):
    if len(kw) > 0:
        return kw['measurement'].description
    return ''

@colander.deferred
def deferred_interval_default(node, kw):
    if len(kw) > 0:
        return kw['measurement'].interval
    return 0.1

@colander.deferred
def deferred_location_widget(node, kw):
    locations = Field_Controller_Session.query(Location).all()
    choises = []
    for l in locations:
        choises.append((l._id, l.name))
    return SelectWidget(values=choises)

@colander.deferred
def deferred_measurand_widget(node, kw):
    measurands = Field_Controller_Session.query(Measurand).all()
    choises = []
    for m in measurands:
        choises.append((m._id, m.name+' ['+m.unit+']'))
    return SelectWidget(values=choises)

@colander.deferred
def deferred_sensor_widget(node, kw):
    sensors = Field_Controller_Session.query(Sensor).all()
    choises = []
    for s in sensors:
        choises.append((s._id, s.controller.name+'->'+s.name))
    return SelectWidget(values=choises)

class MeasurementSchema(MappingSchema):
    location = SchemaNode(typ=Int(),
                      title='Location',
                      description='Place where the measurement is taken',
                      default=deferred_location_default,
                      widget=deferred_location_widget)
    measurand = SchemaNode(typ=Int(),
                      title='Measurand',
                      description='what is beeing measured',
                      default=deferred_measurand_default,
                      widget=deferred_measurand_widget)
    sensor = SchemaNode(typ=Int(),
                        title='Sensor',
                        default=deferred_sensor_default,
                        widget=deferred_sensor_widget)
    interval = SchemaNode(typ=Float(),
                           title='Measurement Interval [s]',
                           validation=Range(0, 10),
                           default=deferred_interval_default,
                           widget=TextInputWidget())
    description = SchemaNode(typ=String(),
                             title='Description',
                             description='additional information about the measurand',
                             validation=Length(max=250),
                             default=deferred_description_default,
                             widget=TextInputWidget(),
                             missing=None)