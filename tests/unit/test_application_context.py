import os

from nose.tools import eq_

from chatmotor import application_context


class TestApplicationContext(object):

    def test_context_is_initialization_with_bindings(self):
        self._init_context_with_mock_bindings()
        eq_(type(self.context.get("mock_object")).__name__, "MockObject")

    def _init_context_with_mock_bindings(self):
        self.context = application_context.ApplicationContext()
        self.context.initialize(os.path.join(os.path.dirname(os.path.realpath(__file__)), "mock_bindings.py"))
