import logging
import uuid

import injector
import pika

logger = logging.getLogger(__name__)


class PikaClientForTornado(object):

    @injector.inject(configuration="configuration", connection_class="pika_connection_class")
    def __init__(self, configuration, connection_class):
        self.configuration = configuration
        self.connection_class = connection_class

    def connect(self):
        logger.info('PikaClientForTornado: Connecting to RabbitMQ')

        rabbit_credentials = pika.PlainCredentials(
            self.configuration.get('RABBIT_USERID'),
            self.configuration.get('RABBIT_PASSWORD'))

        rabbit_connection_params = pika.ConnectionParameters(
            host=self.configuration.get('RABBIT_HOST'),
            port=self.configuration.get('RABBIT_PORT'),
            virtual_host="/",
            credentials=rabbit_credentials)

        self.tornado_connection = self.connection_class(
            rabbit_connection_params, on_open_callback=self._on_pika_connected)

    def _on_pika_connected(self, connection):
        logger.debug('Connected to Rabbit')

        self.connection = connection
        self.connection.channel(self._on_pika_channel_open)
        self.connection.add_on_close_callback(self._on_pika_closed)

    def _on_pika_closed(self, connection):
        logger.warn('Tornado connection closed.')

    def _on_pika_channel_open(self, channel):
        logger.debug('Channel Open')
        self.channel = channel
        self.configure_broker()

    def configure_broker(self):
        # This doesn't feel right. It belongs somewhere else. Will wait till we do other things to
        # the channel and an appropriate pattern will emerge.
        self.declare_direct_exchange(self.configuration.get('INSTANT_MESSAGE_EXCHANGE_NAME'))

    def declare_direct_exchange(self, exchange_name):
        self.channel.exchange_declare(
            exchange=exchange_name,
            type="direct",
            callback=lambda arg: logger.info("Exchange succesfully declared."))

    def publish_message(self, exchange_name, routing_key, message):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=message)

    def declare_exclusive_queue(self, queue_name, callback):
        self.channel.queue_declare(exclusive=True, queue=queue_name, callback=callback)

    def unbind_queue(self, queue_name, exchange_name, routing_key, callback):
        self.channel.queue_unbind(
            callback=callback,
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key)

    def bind_queue(self, exchange_name, queue_name, routing_key, callback):
        self.channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key,
            callback=callback)

    def consume_queue(self, queue_name, on_message_callback):
        self.channel.basic_consume(
            consumer_callback=on_message_callback,
            queue=queue_name,
            no_ack=True)

    def delete_queue(self, queue_name):
        self.channel.queue_delete(
            callback=lambda arg: logger.debug("Queue deleted."),
            queue=queue_name)


class ImMessagePublisher(object):

    @injector.inject(broker_client="msg_broker_client", configuration="configuration")
    def __init__(self, broker_client, configuration):
        self.im_exchange_name = configuration.get('INSTANT_MESSAGE_EXCHANGE_NAME')
        self.broker_client = broker_client

    def send_message(self, recipient_username, message_body):
        self.broker_client.publish_message(self.im_exchange_name, recipient_username, message_body)


class ImIncomingQueue(object):

    @injector.inject(broker_client="msg_broker_client", configuration="configuration")
    def __init__(self, broker_client, configuration):
        self.im_exchange_name = configuration.get('INSTANT_MESSAGE_EXCHANGE_NAME')
        self.queue_name = str(uuid.uuid1())
        self.broker_client = broker_client

    def open_message_queue(self, username, on_msg_received):
        self.on_message_received = on_msg_received
        self.routing_key = username
        self.broker_client.declare_exclusive_queue(self.queue_name, self._bind_queue)

    def close_message_queue(self):
        self.broker_client.unbind_queue(self.queue_name, self.im_exchange_name, self.routing_key, self._delete_queue)

    def _bind_queue(self, x):
        self.broker_client.bind_queue(self.im_exchange_name, self.queue_name, self.routing_key, self._begin_consume)

    def _begin_consume(self, frame):
        self.broker_client.consume_queue(self.queue_name, self._on_queue_message_received)

    def _on_queue_message_received(self, channel, method, header, body):
        self.on_message_received(body)

    def _delete_queue(self, method):
        self.broker_client.delete_queue(self.queue_name)
