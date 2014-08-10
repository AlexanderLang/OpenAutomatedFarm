import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from ..models import DBSession
from ..models import Base

from ..models import init_parameters
from ..models import init_parameter_types
from ..models import init_devices
from ..models import init_device_types
from ..models import init_plant_settings
from ..models import init_stages
from ..models import init_stage_configurations
from ..models import init_farm_components
from ..models import init_field_settings


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
        init_farm_components(DBSession)
        init_parameter_types(DBSession)
        init_parameters(DBSession)
        init_device_types(DBSession)
        init_devices(DBSession)
        init_plant_settings(DBSession)
        init_stages(DBSession)
        init_stage_configurations(DBSession)
        init_field_settings(DBSession)
