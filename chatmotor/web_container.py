import logging

import injector

logger = logging.getLogger(__name__)


class WebContainer(object):

    @injector.inject(http_server="http_server", ioloop="ioloop")
    def __init__(self, http_server, ioloop):
        self.http_server = http_server
        self.ioloop = ioloop

    def start(self):
        self.ioloop.start()

    def stop(self):
        self.ioloop.stop()
