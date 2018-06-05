from config import EVENT_TYPE
import re
import random
import subprocess
from utils import get_bound_from_string

# def get_click_point_from_bound(bound):
#     return ((bound[0] + bound[1])/2, (bound[2] + bound[3])/2)


def get_scroll_point_from_bound(bound):
    horizontal_center = (bound[0] + bound[1]) / 2
    return horizontal_center, bound[3], horizontal_center, bound[2] #scroll from top to bottom or bottom to top ?


class Executor(object):
    device = None
    package = None

    def __init__(self, device, package):
        self.device = device
        self.package = package

    def start_activity(self, package, activity):
        output = subprocess.check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(package, activity)])
        return output

    # TODO change
    def gen_random_text(self):
        """Gen random text."""
        le = (random.randint(1, 16))
        choice = (random.randint(0, 10))
        arr = []
        if choice == 0 or choice == 4 or choice == 5:
            arr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        elif choice == 1:
            arr = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        elif choice == 2:
            arr = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        elif choice == 3:
            arr = list('(*&^%$#@!{abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
        elif choice == 6:
            return 'DEL'
        else:
            return ''
        return ''.join(random.choice(arr) for x in range(le))

    # TODO review

    def del_text(self, count):
        """ADB del."""
        subprocess.call(
                ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_MOVE_END'])
        for i in range(count):
            subprocess.call(
                ['adb', 'shell', 'input', 'keyevent', 'KEYCODE_DEL'])

    def enter_text(self, text):
        """Fire a text event."""
        if len(text) == 0:
            return
        elif text == 'DEL':
            self.del_text(random.randint(1, 20))
        else:
            subprocess.call(['adb', 'shell', 'input', 'keyboard', 'text', '"'+text+'"'])
            subprocess.call(['adb', 'shell', 'input', 'keyevent', '111'])

    def perform_action(self, component):
        """
        perform action on component
        component is a tuple (gui_type, event_type, bounds)
        :param component:
        :return:
        """
        bound = get_bound_from_string(component[2])
        if component[1] not in EVENT_TYPE:
            return None
        else:
            if component[1] == "click" or component[1] == "check":
                self.device.click((bound[0] + bound[1])/2, (bound[2] + bound[3])/2)
            elif component[1] == "long-click":
                self.device.long_click((bound[0] + bound[1])/2, (bound[2] + bound[3])/2)
            elif component[1] == "scroll":
                self.device.drag(get_scroll_point_from_bound(bound))
            elif component[1] == "text":
                self.device.click((bound[0] + bound[1])/2, (bound[2] + bound[3])/2)
                self.enter_text(self.gen_random_text())

    def press_back(self):
        self.device.press.back()

    def press_menu(self):
        self.device.press.home()

    def start_activity(self, activity):
        output = subprocess.check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(self.package, activity)])
        print(output)
        return output



