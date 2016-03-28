import mock
from nose.tools import eq_

from chatmotor import pika_client


class TestImMessagePublisher(object):

    def setup(self):
        self.broker_mock = mock.Mock()
        self.configuration_mock = mock.Mock()
        self.publisher = pika_client.ImMessagePublisher(self.broker_mock, self.configuration_mock)

    def test_send_message_passed_to_broker(self):
        self.publisher.send_message(mock.sentinel.USERNAME, mock.sentinel.MSG_BODY)

        expected_call_to_broker_client = mock.call(
            self.configuration_mock.get('INSTANT_MESSAGE_EXCHANGE_NAME'),
            mock.sentinel.USERNAME, mock.sentinel.MSG_BODY)

        eq_([expected_call_to_broker_client], self.broker_mock.publish_message.call_args_list)


class TestImIncomingQueue(object):

    def setup(self):
        self.broker_mock = mock.Mock()
        self.configuration_mock = mock.Mock()
        self.mock_on_msg_received_callback = mock.Mock()
        self.im_queue = pika_client.ImIncomingQueue(self.broker_mock, self.configuration_mock)

    def test_open_message_queue_routing_key_set_as_username(self):
        self.im_queue.open_message_queue(mock.sentinel.USERNAME, self.mock_on_msg_received_callback)
        eq_(self.im_queue.routing_key, mock.sentinel.USERNAME)

    def test_open_message_queue_saves_on_msg_callback(self):
        self.im_queue.open_message_queue(mock.sentinel.USERNAME, self.mock_on_msg_received_callback)
        eq_(self.mock_on_msg_received_callback, self.im_queue.on_message_received)

    def test_open_message_queue_calls_broker_client_to_declare_queue(self):
        self.im_queue.open_message_queue(mock.sentinel.USERNAME, self.mock_on_msg_received_callback)
        expected_call_args_to_broker_client = mock.call(self.im_queue.queue_name, self.im_queue._bind_queue)
        eq_([expected_call_args_to_broker_client], self.broker_mock.declare_exclusive_queue.call_args_list)
