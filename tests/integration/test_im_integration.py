import json
import time

from nose.tools import eq_
from websocket import create_connection


BASE_WEBSOCKET_URL = "ws://localhost:8888"
WEBSOCKET_TIMEOUT_SEC = 2


def _simulate_client_delay():
    time.sleep(0.1)

ALICE = "alice"
BOB = "bob"


class TestInstantMessagesSanity(object):

    def test_alice_can_connect_again_after_disconnecting_and_send_herself_a_message(self):
        ws_alice = None

        try:
            ws_alice = _create_im_connection(ALICE)
            _simulate_client_delay()
            _close_if_not_none(ws_alice)

            ws_alice = _create_im_connection(ALICE)
            _simulate_client_delay()

            ws_alice.send(json.dumps(_create_im_payload(ALICE, ALICE, "hello world")))
            _simulate_client_delay()

            _assert_expected_payload_recieved(ws_alice,  _create_im_payload(ALICE, ALICE, "hello world"))

        finally:
            _close_if_not_none(ws_alice)

    def test_alice_sends_message_to_alice(self):
        ws_alice = None

        try:
            ws_alice = _create_im_connection(ALICE)
            _simulate_client_delay()

            ws_alice.send(json.dumps(_create_im_payload(ALICE, ALICE, "hello world")))
            _simulate_client_delay()

            _assert_expected_payload_recieved(ws_alice,  _create_im_payload(ALICE, ALICE, "hello world"))

        finally:
            _close_if_not_none(ws_alice)

    def test_alice_sends_message_to_bob(self):
        ws_alice = None
        ws_bob = None

        try:
            ws_alice = _create_im_connection(ALICE)
            ws_bob = _create_im_connection(BOB)
            _simulate_client_delay()

            ws_alice.send(json.dumps(_create_im_payload(ALICE,  BOB, "hello bob")))
            _simulate_client_delay()

            eq_(json.dumps(_create_im_payload(ALICE, BOB, "hello bob")), ws_bob.recv())

        finally:
            _close_if_not_none(ws_alice)
            _close_if_not_none(ws_bob)

    def test_alice_sends_message_to_bob_then_disconnects_and_bob_receives_the_message(self):
        ws_alice = None
        ws_bob = None

        try:
            ws_alice = _create_im_connection(ALICE)
            ws_bob = _create_im_connection(BOB)
            _simulate_client_delay()

            ws_alice.send(json.dumps(_create_im_payload(ALICE,  BOB, "hello bob")))
            _close_if_not_none(ws_alice)

            _simulate_client_delay()

            eq_(json.dumps(_create_im_payload(ALICE, BOB, "hello bob")), ws_bob.recv())

        finally:
            _close_if_not_none(ws_bob)

    def test_alice_sends_multiple_messages_to_bob_and_bob_replies_to_alice(self):
        ws_alice = None
        ws_bob = None

        try:
            ws_alice = _create_im_connection(ALICE)
            ws_bob = _create_im_connection(BOB)
            _simulate_client_delay()

            for message_num in range(1, 10):
                ws_alice.send(json.dumps(_create_im_payload(ALICE,  BOB, "hello bob {}".format(message_num))))

            _simulate_client_delay()

            for message_num in range(1, 10):
                eq_(json.dumps(_create_im_payload(ALICE, BOB, "hello bob {}".format(message_num))), ws_bob.recv())
                ws_alice.send(json.dumps(_create_im_payload(BOB, ALICE, "thanks alice {}".format(message_num))))

            _simulate_client_delay()

            for message_num in range(1, 10):
                eq_(json.dumps(_create_im_payload(BOB, ALICE, "thanks alice {}".format(message_num))), ws_alice.recv())

        finally:
            _close_if_not_none(ws_alice)
            _close_if_not_none(ws_bob)


def _close_if_not_none(websocket):
    if websocket is not None:
        websocket.close()


def _receive_and_ignore(websocket):
    websocket.recv()


def _create_im_connection(username, timeout=WEBSOCKET_TIMEOUT_SEC):
    return create_connection("{}/im/{}".format(BASE_WEBSOCKET_URL, username), timeout)


def _create_im_payload(sender, destination, msg_content):
    return {
        "sender": sender,
        "destination": destination,
        "payload": msg_content,
        "type": "instant_message"
    }


def _assert_expected_payload_recieved(websocket, expected):
    eq_(expected, json.loads(websocket.recv()))
