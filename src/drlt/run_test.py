import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import errno
import random
import subprocess
import re
import time

from observer import observer
from executor import executor
from executor.executor import get_bound_from_string
from config import DEVICE
from uiautomator import Device
from subprocess import check_output


STEP = 50
APP_NAME = "_Users_tuyetvuong_fdroidapk_com.angrydoughnuts.android.alarmclock_14.apk"
PACKAGE = "com.angrydoughnuts.android.alarmclock"
LAUNCHER = "AlarmClockActivity"

def get_index_from_bounds(bounds, step_width, step_height):
    left_index = int(bounds[0] / step_width)
    right_index = int(bounds[1] / step_width)
    top_index = int(bounds[2] / step_height)
    bottom_index = int(bounds[3] / step_height)
    return top_index, bottom_index, left_index, right_index

def start_activity(package, activity):
    output = check_output(['adb', 'shell', 'am', 'start', '-n', '{}/.{}'.format(package, activity)])
    print(output)
    return output


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_coverage(app_name):
    output = str(subprocess.check_output(['python', 'tools/tool_coverage.py', app_name, 'method'], cwd="../ella/"))
    c = re.findall(r'\d+', output)[0]
    return c


if __name__ == "__main__":
    # TODO check if device is connected
    device = Device(DEVICE)
    observer = observer.Observer(device, PACKAGE)
    executor = executor.Executor(device, PACKAGE)

    # gui = observer.get_gui_state()[0]
    # INPUT_SIZE = (150, 100)
    # device_info = device.info
    # phone_size = (device_info["displayHeight"], device_info["displayWidth"])
    # step_height = phone_size[0] / INPUT_SIZE[0]
    # step_width = phone_size[1]/INPUT_SIZE[1]
    # x = np.zeros(INPUT_SIZE)
    # for component in gui:
    #     bounds = get_bound_from_string(component[2])
    #     top_index, bottom_index, left_index, right_index = get_index_from_bounds(bounds, step_width, step_height)
    #     # print(top_index, bottom_index, left_index, right_index)
    #     x[top_index:bottom_index + 1, left_index:right_index + 1] = x[top_index:bottom_index+1, left_index:right_index+1] +1

    # plt.gray()
    # plt.imshow(np.uint8(x))
    # plt.show()

    start_activity(PACKAGE, LAUNCHER)
    out_dir = "./{}/".format(PACKAGE)
    out_file = "./{}/out.txt".format(PACKAGE)
    mkdir_p(out_dir)
    with open(out_file, "a") as f:
        for i in range(STEP):
            time.sleep(0.5)
            k = 0
            while (not observer.is_in_app()) and k < 5:
                executor.press_back()
                k = k + 1
            if not observer.is_in_app():
                start_activity(PACKAGE, LAUNCHER)
            else:
                s1 = observer.get_gui_state()[0]
                c1 = float(get_coverage(APP_NAME))
                a = random.choice(s1)
                executor.perform_action(a)
                s2 = observer.get_gui_state()[0]
                c2 = float(get_coverage(APP_NAME))
                r = c2-c1
                print((a, r))
                f.write(str((s1, a, r, s2)) +"\n")

#     TODO deal with the recent activity







