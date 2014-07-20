import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from pyramid.scripts.common import parse_vars

from ..models.plant_settings import DBSession as Plant_Settings_Session
from ..models.plant_settings import Base as PlantSettings_Base
from ..models.plant_settings import init_Parameters
from ..models.plant_settings import init_PlantSettings
from ..models.plant_settings import init_Stages
from ..models.plant_settings import init_StageConfigurations

from ..models.field_controller import DBSession as Field_Controller_Session
from ..models.field_controller import Base as FieldController_Base
from ..models.field_controller import init_Locations
from ..models.field_controller import init_Measurands
from ..models.field_controller import init_PeripheryControllers
from ..models.field_controller import init_Sensors
from ..models.field_controller import init_Measurements
from ..models.field_controller import init_FieldSettings

def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <config_uri> [var=value]\n'
		  '(example: "%s development.ini")' % (cmd, cmd))
	sys.exit(1)


def main(argv=sys.argv):
	if len(argv) < 2:
		usage(argv)
	config_uri = argv[1]
	options = parse_vars(argv[2:])
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)
	
	plant_settings_engine = engine_from_config(settings, 'plant_settings_database.')
	Plant_Settings_Session.configure(bind=plant_settings_engine)
	PlantSettings_Base.metadata.create_all(plant_settings_engine)
	
	field_controller_engine = engine_from_config(settings, 'field_controller_database.')
	Field_Controller_Session.configure(bind=field_controller_engine)
	FieldController_Base.metadata.create_all(field_controller_engine)
	
	# populate databases
	with transaction.manager:
		# Plant Settings
		init_Parameters(Plant_Settings_Session)
		init_PlantSettings(Plant_Settings_Session)
		init_Stages(Plant_Settings_Session)
		init_StageConfigurations(Plant_Settings_Session)
		# Field Controller
		init_Locations(Field_Controller_Session)
		init_Measurands(Field_Controller_Session)
		init_PeripheryControllers(Field_Controller_Session)
		init_Sensors(Field_Controller_Session)
		init_Measurements(Field_Controller_Session)
		init_FieldSettings(Field_Controller_Session)
		
