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
from config import DEVICE, EPISODE_LENGTH
from uiautomator import Device
from subprocess import check_output
from preprocess import preprocess


APP_NAME = "_Users_tuyetvuong_fdroidapk_com.angrydoughnuts.android.alarmclock_14.apk"
PACKAGE = "com.angrydoughnuts.android.alarmclock"
LAUNCHER = "AlarmClockActivity"

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
    preprocess = preprocess.Preprocess(device)

    gui = observer.get_gui_state()[0]
    x = preprocess.create_input_matrix(gui)

    start_activity(PACKAGE, LAUNCHER)
    out_dir = "./{}/".format(PACKAGE)
    out_file = "./{}/out.txt".format(PACKAGE)
    mkdir_p(out_dir)
    with open(out_file, "a") as f:
        for i in range(EPISODE_LENGTH):
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







