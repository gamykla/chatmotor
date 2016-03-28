from pika.adapters import tornado_connection
from injector import InstanceProvider, ClassProvider, singleton, noscope

from chatmotor.controllers import instant_message_websockets
from chatmotor import pika_client
from chatmotor import settings
from chatmotor import web_container


class IOLoopInstanceProvider(InstanceProvider):

    def __init__(self):
        super(IOLoopInstanceProvider, self).__init__(None)

    def get(self, injector=None):
        import tornado.ioloop
        import time

        broker_client = injector.get('msg_broker_client')
        ioloop = tornado.ioloop.IOLoop.instance()
        ioloop.add_timeout(time.time() + 0.01, broker_client.connect)
        return ioloop


class HTTPServerInstanceProvider(InstanceProvider):

    def __init__(self):
        super(HTTPServerInstanceProvider, self).__init__(None)

    def get(self, injector=None):
        from chatmotor.controllers import instant_message_websockets
        import tornado

        configuration = injector.get("configuration")
        request_mapping = [(r'/im/(.*)', instant_message_websockets.InstantMessageWebSocketController)]
        tornado_webapp = tornado.web.Application(request_mapping, configuration.get('HTTP_SETTINGS'))
        tornado_webapp.listen(configuration.get('TORNADO_LISTEN_PORT'))
        return tornado_webapp

interface_bindings = {
    "web_container": {"to": ClassProvider(web_container.WebContainer), "scope": singleton},
    "ioloop": {"to": IOLoopInstanceProvider(), "scope": singleton},
    "http_server": {"to": HTTPServerInstanceProvider(), "scope": singleton},
    "configuration": {"to": InstanceProvider(settings.read_configuration()), "scope": singleton},
    "msg_broker_client": {"to": ClassProvider(pika_client.PikaClientForTornado), "scope": singleton},
    "instant_messenger": {"to": ClassProvider(instant_message_websockets.InstantMessenger), "scope": noscope},
    "im_incoming_queue": {"to": ClassProvider(pika_client.ImIncomingQueue), "scope": noscope},
    "im_message_publisher": {"to": ClassProvider(pika_client.ImMessagePublisher), "scope": noscope},
    "pika_connection_class": {"to": InstanceProvider(tornado_connection.TornadoConnection), "scope": noscope},
}
