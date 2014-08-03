from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession
from .models import Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings)
    config.add_static_view(name='static', path='farmgui:static', cache_max_age=3600)
    config.add_static_view(name='deform_static', path='deform:static', cache_max_age=3600)
    config.include(add_routes)
    config.scan()
    return config.make_wsgi_app()


def add_routes(config):
    # project views
    config.add_route('project_views_root', '/')
    config.add_route('project_views_home', '/farm/home')
    config.add_route('project_views_about', '/farm/about')
    # configuration views
    config.add_route('configuration_views_home', '/configuration')
    config.add_route('components_list', '/configuration/components')
    config.add_route('parameter_save', '/configuration/parameters/add')
    config.add_route('parameter_delete', '/configuration/parameters/{_id}/delete')
    config.add_route('parameter_update', '/configuration/parameters/{_id}/update')
    config.add_route('component_delete', '/configuration/component/{_id}/delete')
    config.add_route('component_save', '/configuration/component/{_id}/save')
    config.add_route('field_settings_list', '/configuration/field_settings')
    config.add_route('field_setting_update', '/configuration/field_settings/{name}/update')
    config.add_route('periphery_controllers_list', '/configuration/periphery_controllers')
    config.add_route('periphery_controller_update', '/configuration/periphery_controllers/{_id}/update')

    config.add_route('plant_settings_list', '/plant_settings')
    config.add_route('plant_settings_new', '/plant_settings/add')
    config.add_route('plant_settings_view', '/plant_settings/plant/{_id}')
    config.add_route('parameters_list', '/plant_settings/parameters')
    config.add_route('parameters_new', '/plant_settings/parameters/add')
    config.add_route('stage_new', '/plant_settings/stages/{_id}/new_stage')
    config.add_route('stage_view', '/plant_settings/stages/{_id}')
    config.add_route('stage_configuration_new', '/plant_settingsstages/{_id}/new_configuration')
    config.add_route('stage_configurations_data', '/plant_settings/stages/{_id}/configurations_data')

    config.add_route('measurements_new', '/config/measurements/new')
    config.add_route('measurement_view', '/config/measurements/{measurement_id}')
    config.add_route('measurements_list', '/config/measurements/')

    config.add_route('sensor_view', '/field_controller/sensors/{_id}')

    config.add_route('measurement_log_json', '/json/measurements/{measurement_id}/logs')
