from config import EVENT_TYPE
import re
from subprocess import check_output


def get_bound_from_string(bound_string):
    coordinate = re.findall(r'\d+', bound_string)
    left = int(coordinate[0])
    top = int(coordinate[1])
    right = int(coordinate[2])
    bottom = int(coordinate[3])
    return [left, right, top, bottom]


def get_click_point_from_bound(bound):
    return ((bound[0] + bound[1]) / 2, (bound[2] + bound[3]) / 2)


def get_scroll_point_from_bound(bound):
    horizontal_center = (bound[0] + bound[1]) / 2
    return horizontal_center, bound[2], horizontal_center, bound[3]


class Executor(object):
    device = None

    def __init__(self, device):
        self.device = device

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
                pass

    def start_activity(self, package, activity):
        output = check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(package, activity)])
        print(output)
        return output

    def press_back(self):
        self.device.back()

    def press_menu(self):
        self.device.home()

    def get_current_activity(self, package):
        """Get current activity of current package."""
        output = check_output(['adb', 'shell', 'dumpsys', 'window',
                               'windows', '|', 'grep', '-E',
                               "'mCurrentFocus'"])
        cur_activity = output.split('/')[-1].replace(package+'.', '').split('}')[0]
        return cur_activity

    def is_in_app(self, package):
        output = check_output(['adb', 'shell', 'dumpsys', 'window',
                               'windows', '|', 'grep', '-E',
                               "'mCurrentFocus'"])
        if package in output:
            return True
        return False


