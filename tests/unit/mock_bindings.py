from injector import InstanceProvider
from injector import singleton


class MockObject(object):
    pass

mock_object = MockObject()

interface_bindings = {
    "mock_object": {"to": InstanceProvider(mock_object), "scope": singleton},
}
