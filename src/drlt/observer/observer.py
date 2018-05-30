from config import *
import subprocess
import xml.etree.ElementTree as ET


class Observer(object):
    device = None
    package = None

    def __init__(self, device, package):
        self.device = device
        self.package = package

    def get_current_activity(self):
        """Get current activity of current package."""
        output = subprocess.check_output(['adb', 'shell', 'dumpsys', 'window',
                               'windows', '|', 'grep', '-E',
                               "'mCurrentFocus'"])
        cur_activity = output.split('/')[-1].replace(self.package+'.', '').split('}')[0]
        return cur_activity

    def is_in_app(self):
        output = str(subprocess.check_output(['adb', 'shell', 'dumpsys', 'window',
                               'windows', '|', 'grep', '-E',
                               "'mCurrentFocus'"]))
        if self.package in output:
            return True
        print("OUT OF APP {}".format(output))

        return False

    def get_gui_state(self):
        """
        Return the current GUI state, i.e the tuple of GUI components at that state
        A GUI component is defined by a tuple (gui_type, event_type, coordinate). We don't care about content
        :return: GUI state - tuple
        """
        xml = self.device.dump()
        root = ET.fromstring(xml)
        gui_state = ()
        event_type_count = {"click": 0, "long-click": 0, "check": 0, "scroll": 0}
        for node in root.findall(".//*[@clickable='true']"):
            event_type_count["click"] += 1
            # TODO: Distinguish back, menu, normal button, text_input
            gui_state += ((node.attrib["class"], "click", node.attrib["bounds"]),)
        for node in root.findall(".//*[@long-clickable='true']"):
            event_type_count["long-click"] += 1
            gui_state += ((node.attrib["class"], "long-click", node.attrib["bounds"]),)
        for node in root.findall(".//*[@checkable='true']"):
            event_type_count["check"] += 1
            gui_state += ((node.attrib["class"], "check", node.attrib["bounds"]),)
        for node in root.findall(".//*[@scrollable='true']"):
            event_type_count["scroll"] += 1
            gui_state += ((node.attrib["class"], "scroll", node.attrib["bounds"]),)
        return gui_state, tuple(event_type_count.items())

    def get_battery_status(self):
        """
        Get the battery percentage of the current state
        :return: battery percentage
        """
        output = str(subprocess.check_output(['adb', 'shell', 'dumpsys', 'battery', '|', 'grep', 'level']))
        return int(output.split(":")[1].strip())

    def get_network_status(self):
        """
        Get the network status of the current state
        :return: bool (on/off)
        """
        output = str(subprocess.check_output(['adb', 'shell', 'dumpsys', 'connectivity', '|', 'grep', '\'Active default network\'']))
        return output.split(":")[1].strip() != "none"

    def get_current_state(self):
        # state = ("number_of_gui_components", "number_of_event_type", "has_fragment_dialog", "network", "battery", "orientation")
        return self.get_gui_state() + (self.get_network_status(),) + (self.get_battery_status(),)



