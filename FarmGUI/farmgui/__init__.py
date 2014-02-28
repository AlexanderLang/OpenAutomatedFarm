from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from plant_settings_database import DBSession
from plant_settings_database import Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'plant_settings_database.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'farmgui:static', cache_max_age=3600)
    config.include(add_routes)
    config.scan()
    return config.make_wsgi_app()

def add_routes(config):
    config.add_route('home_view', '/')
    config.add_route('about_view', '/about')
    config.add_route('plant_settings_list', '/plant_settings')
    config.add_route('plant_settings_new', '/plant_settings/add')
    config.add_route('plant_settings_view', '/plant_settings/{_id}')
    config.add_route('stage_new', '/plant_settings/{_id}/stage_new')
    config.add_route('stage_view', '/stages/{_id}')
