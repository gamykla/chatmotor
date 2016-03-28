from chatmotor.controllers import instant_message_websockets


class TestInstantMessenger(object):

    def setup(self):
        self.instant_messenger = instant_message_websockets.InstantMessenger()
