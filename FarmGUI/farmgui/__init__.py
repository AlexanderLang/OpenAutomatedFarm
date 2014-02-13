from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from plant_settings_database import DBSession
from plant_settings_database import Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'views/static', cache_max_age=3600)
    config.include(add_routes)
    config.scan()
    return config.make_wsgi_app()

def add_routes(config):
    config.add_route('home', '/')
    config.add_route('about', '/about')
