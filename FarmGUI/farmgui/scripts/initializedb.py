import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
	get_appsettings,
	setup_logging,
	)

from pyramid.scripts.common import parse_vars

from plant_settings_database import DBSession as PlantSettings_Session
from plant_settings_database import Base as PlantSettings_Base
from plant_settings_database import init_Parameters

from field_controller_database import DBSession as FieldController_Session
from field_controller_database import Base as FieldController_Base

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
	PlantSettings_Session.configure(bind=plant_settings_engine)
	PlantSettings_Base.metadata.create_all(plant_settings_engine)
	
	field_controller_engine = engine_from_config(settings, 'field_controller_database.')
	FieldController_Session.configure(bind=field_controller_engine)
	FieldController_Base.metadata.create_all(field_controller_engine)
	
	with transaction.manager:
		init_Parameters(PlantSettings_Session)
		pass
