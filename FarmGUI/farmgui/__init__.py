from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from plant_settings_database import DBSession as Plant_Settings_Session
from plant_settings_database import Base as Plant_Settings_Base

from field_controller_database import DBSession as Field_Controller_Session
from field_controller_database import Base as Field_Controller_Base

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    plant_settings_engine = engine_from_config(settings, 'plant_settings_database.')
    Plant_Settings_Session.configure(bind=plant_settings_engine)
    Plant_Settings_Base.metadata.bind = plant_settings_engine
    
    field_controller_engine = engine_from_config(settings, 'field_controller_database.')
    Field_Controller_Session.configure(bind=field_controller_engine)
    Field_Controller_Base.metadata.bind = field_controller_engine
    
    config = Configurator(settings=settings)
    config.add_static_view(name='static', path='farmgui:static', cache_max_age=3600)
    config.add_static_view(name='deform_static', path='deform:static', cache_max_age=3600)
    config.include(add_routes)
    config.scan()
    return config.make_wsgi_app()

def add_routes(config):
    config.add_route('home_view', '/')
    config.add_route('about_view', '/about')
    
    config.add_route('plant_settings_list', '/plant_settings')
    config.add_route('plant_settings_new', '/plant_settings/add')
    config.add_route('plant_settings_view', '/plant_settings/plant/{_id}')
    config.add_route('parameters_list', '/plant_settings/parameters')
    config.add_route('parameters_new', '/plant_settings/parameters/add')
    config.add_route('stage_new', '/plant_settings/stages/{_id}/new_stage')
    config.add_route('stage_view', '/plant_settings/stages/{_id}')
    config.add_route('stage_configuration_new', '/plant_settingsstages/{_id}/new_configuration')
    config.add_route('stage_configurations_data', '/plant_settings/stages/{_id}/configurations_data')
    
    config.add_route('field_settings_list', '/field_controller')
    config.add_route('measurements_list', '/field_controller/measurements')
    config.add_route('measurements_new', '/field_controller/measurements/new')
    config.add_route('measurement_view', '/field_controller/measurements/{measurement_id}')
    config.add_route('measurement_log_json', '/field_controller/measurements/{measurement_id}/logs_json')
    config.add_route('periphery_controllers_list', '/field_controller/periphery_controllers')
    config.add_route('periphery_controller_view', '/field_controller/periphery_controllers/{_id}')
    config.add_route('sensor_view', '/field_controller/sensors/{_id}')
