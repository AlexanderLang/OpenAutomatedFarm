import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from farmgui.models import DBSession
from farmgui.models import Base
from farmgui.models import init_setpoint_interpolations
from farmgui.models import init_parameters
from farmgui.models import init_parameter_types
from farmgui.models import init_devices
from farmgui.models import init_device_types
from farmgui.models import init_field_settings
from farmgui.models import init_regulators
from farmgui.models import init_periphery_controllers


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
        init_setpoint_interpolations(DBSession)
        init_parameter_types(DBSession)
        init_device_types(DBSession)
        init_periphery_controllers(DBSession)
        init_parameters(DBSession)
        init_devices(DBSession)
        init_field_settings(DBSession)
        init_regulators(DBSession)
