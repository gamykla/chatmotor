import json
import logging

import injector
import tornado.websocket as websocket

from chatmotor import global_context

logger = logging.getLogger(__name__)


class InstantMessenger(object):

    @injector.inject(im_incoming_queue="im_incoming_queue", im_message_publisher="im_message_publisher")
    def __init__(self, im_incoming_queue, im_message_publisher):
        self.im_incoming_queue = im_incoming_queue
        self.im_message_publisher = im_message_publisher

    def start_im_session(self, on_msg_recv, username):
        self.im_incoming_queue.open_message_queue(username, on_msg_recv)

    def send_im(self, recipient_name, message_json):
        self.im_message_publisher.send_message(recipient_name, message_json)

    def stop_im_session(self):
        self.im_incoming_queue.close_message_queue()


class InstantMessageWebSocketController(websocket.WebSocketHandler):

    def open(self, username):
        self.instant_messenger = global_context.application_context.get("instant_messenger")
        self.instant_messenger.start_im_session(self._on_im_received, username)

    def on_message(self, message):
        message_json = json.loads(message)
        self.instant_messenger.send_im(message_json["destination"], message)

    def _on_im_received(self, body):
        self.write_message(body)

    def on_close(self):
        self.instant_messenger.stop_im_session()
