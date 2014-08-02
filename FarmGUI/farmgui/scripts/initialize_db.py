import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from ..models import DBSession
from ..models import Base

from ..models import init_Parameters
from ..models import init_ParameterTypes
from ..models import init_PlantSettings
from ..models import init_Stages
from ..models import init_StageConfigurations
from ..models import init_FarmComponents
from ..models import init_FieldSettings

def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <config_uri> [var=value]\n'
		  '(example: "%s development.ini")' % (cmd, cmd))
	sys.exit(1)


def main(argv=sys.argv):
	if len(argv) < 2:
		usage(argv)
	config_uri = argv[1]
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)
	
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	Base.metadata.create_all(engine)
	
	# populate databases
	with transaction.manager:
		init_FarmComponents(DBSession)
		init_ParameterTypes(DBSession)
		init_Parameters(DBSession)
		init_PlantSettings(DBSession)
		init_Stages(DBSession)
		init_StageConfigurations(DBSession)
		init_FieldSettings(DBSession)
