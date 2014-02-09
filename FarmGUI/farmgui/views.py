from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from plant_settings_database import DBSession
from plant_settings_database import Parameter


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'FarmGUI'}

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_FarmGUI_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

@view_config(route_name='parameters', renderer='templates/parameters.pt')
def parameters(request):
	params = DBSession.query(Parameter)
	return { 'params': params}

