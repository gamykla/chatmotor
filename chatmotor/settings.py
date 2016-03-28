import imp
import os
import logging.config


def _get_configuration_directory():
    return os.environ.get("CM_CONFIG_HOME")


def configure_logging():
    logging.config.fileConfig(
        os.path.join(_get_configuration_directory(), 'logging.cfg'), disable_existing_loggers=False)


def read_configuration():
    configuration_file = os.path.join(_get_configuration_directory(), 'config.py')
    configuration_module = imp.new_module('configuration')
    configuration_module.__file__ = configuration_file
    execfile(configuration_file, configuration_module.__dict__)
    return getattr(configuration_module, 'CONFIGURATION')
