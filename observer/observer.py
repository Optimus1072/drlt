from uiautomator import Device


class Observer(object):
    device = None

    def __init__(self, device):
        self.device = device
