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
    config.add_static_view(name='static', path='farmgui:static', cache_max_age=0)
    config.add_static_view(name='deform_static', path='deform:static', cache_max_age=3600)
    config.add_static_view(name='interpolation_plots', path='farmgui:plots/interpolations', cache_max_age=0)
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
    config.add_route('device_save', '/configuration/devices/add')
    config.add_route('device_delete', '/configuration/devices/{_id}/delete')
    config.add_route('device_update', '/configuration/devices/{_id}/update')
    config.add_route('component_delete', '/configuration/component/{_id}/delete')
    config.add_route('component_save', '/configuration/component/{_id}/save')
    config.add_route('field_settings_list', '/configuration/field_settings')
    config.add_route('field_setting_update', '/configuration/field_settings/{name}/update')
    config.add_route('periphery_controllers_list', '/configuration/periphery_controllers')
    config.add_route('periphery_controller_update', '/configuration/periphery_controllers/{_id}/update')
    # display views
    config.add_route('display_views_home', '/display')
    config.add_route('plot_parameter_data', '/display/parameter/data')
    # calendar views
    config.add_route('calendar_home', '/calendar/{parameter_id}')
    config.add_route('calendar_entry_save', '/calendar/{parameter_id}/save')
    config.add_route('calendar_entry_delete', '/calendar/{parameter_id}/delete/{entry_id}')
    config.add_route('interpolation_save', '/calendar/{parameter_id}/interpolation/save')
    config.add_route('interpolation_update', '/calendar/{parameter_id}/interpolation/{interpolation_id}/update')
    config.add_route('interpolation_delete', '/calendar/{parameter_id}/interpolation/{interpolation_id}/delete')
    config.add_route('interpolation_knot_save', '/calendar/{parameter_id}/interpolation/{interpolation_id}/knot/save')
    config.add_route('interpolation_knot_update', '/calendar/{parameter_id}/interpolation/{interpolation_id}/{knot_id}/update')
    config.add_route('interpolation_knot_delete', '/calendar/{parameter_id}/interpolation/{interpolation_id}/{knot_id}/delete')
