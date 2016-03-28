import imp

from injector import Injector


class ApplicationContext(object):

    def initialize(self, bindings_file):
        interface_bindings_module = imp.new_module('interface_bindings_module')
        interface_bindings_module.__file__ = bindings_file
        execfile(bindings_file, interface_bindings_module.__dict__)
        self._interface_bindings = getattr(interface_bindings_module, 'interface_bindings')

        self.injector = Injector()
        self.injector.binder.install(self.configure)

    def get(self, interface):
        return self.injector.get(interface)

    def configure(self, binder):
        for interface, config in self._interface_bindings.iteritems():
            binder.bind(interface, to=config['to'], scope=config['scope'])
