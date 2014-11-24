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
    config.add_static_view(name='plots', path=settings['plot_directory'], cache_max_age=0)
    config.include(add_routes)
    config.scan()
    return config.make_wsgi_app()


def add_routes(config):
    # project views
    config.add_route('project_views_home',  '/')
    config.add_route('project_views_about', '/about')
    config.add_route('get_redis_values',     '/redis_values')
    # hardware views
    config.add_route('hardware_views_home',         '/hardware')
    config.add_route('periphery_controller_update', '/hardware/pc/update/{pc_id}')
    config.add_route('periphery_controller_delete', '/hardware/pc/delete/{pc_id}')
    # component views
    config.add_route('component_views_home', '/components')
    config.add_route('component_update',       '/components/update/{comp_id}')
    config.add_route('component_delete',       '/components/delete/{comp_id}')
    config.add_route('component_input_update', '/components/input/update/{comp_in_id}')
    config.add_route('component_property_update', '/components/properties/update/{comp_prop_id}')

    config.add_route('parameter_save',         '/components/param/save')
    config.add_route('parameter_update',       '/components/param/update/{param_id}')
    config.add_route('parameter_delete',       '/components/param/delete/{param_id}')

    config.add_route('device_save',            '/components/dev/save')
    config.add_route('device_update',          '/components/dev/update/{dev_id}')
    config.add_route('device_delete',          '/components/dev/delete/{dev_id}')

    config.add_route('regulator_save',         '/components/reg/save')
    config.add_route('regulator_update',       '/components/reg/update/{reg_id}')
    config.add_route('regulator_delete',       '/components/reg/delete/{reg_id}')
    # settings views
    config.add_route('setting_views_home',     '/settings')
    config.add_route('field_setting_update',   '/settings/update/{name}')
    # display views
    config.add_route('display_views_home',    '/display')
    config.add_route('log_diagram_save',      '/display/log_diagram/save')
    config.add_route('log_diagram_update',    '/display/log_diagram/update/{ld_id}')
    config.add_route('log_diagram_delete',    '/display/log_diagram/delete/{ld_id}')
    config.add_route('log_diagram_data',      '/display/log_diagram/data')
    config.add_route('parameter_link_save',   '/display/parameter_link/save/{dis_id}')
    config.add_route('parameter_link_update', '/display/parameter_link/update/{pl_id}')
    config.add_route('parameter_link_delete', '/display/parameter_link/delete/{pl_id}')
    config.add_route('device_link_save',      '/display/device_link/save/{dis_id}')
    config.add_route('device_link_update',    '/display/device_link/update/{dl_id}')
    config.add_route('device_link_delete',    '/display/device_link/delete/{dl_id}')


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
