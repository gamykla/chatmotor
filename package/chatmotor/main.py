import os

from chatmotor import settings
from chatmotor import global_context
from chatmotor import application_context


def run():
    settings.configure_logging()

    global_context.application_context = application_context.ApplicationContext()
    global_context.application_context.initialize(os.environ['CM_BINDINGS'])

    web_container = global_context.application_context.get("web_container")
    web_container.start()
