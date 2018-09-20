from .executor import Executor
from .installer import Installer
from .observer import Observer



class DeviceApp(object):
    def __init__(self, device_name, package):
        device = Device(device_name)
        self.observer = Observer(package, device)
        self.executor = Executor(device)
        self.installer = Installer()
