import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random
import time

from device import observer, executor
from device.observer import get_coverage
from config import DEVICE, EPISODE_LENGTH, EPISODE
from utils import mkdir_p
from uiautomator import Device
from preprocess import preprocess

APP_NAME = "_Users_tuyetvuong_fdroidapk_com.angrydoughnuts.android.alarmclock_14.apk"
PACKAGE = "com.angrydoughnuts.android.alarmclock"
LAUNCHER = "AlarmClockActivity"

MAX_STEP_BACK = 5
if __name__ == "__main__":
    # TODO check if device is connected
    device = Device(DEVICE)
    observer = observer.Observer(device, PACKAGE)
    executor = executor.Executor(device, PACKAGE)
    processor = preprocess.Preprocess(device)

    executor.start_activity(LAUNCHER)
    out_dir = "./{}/".format(PACKAGE)
    out_file = "./{}/out.txt".format(PACKAGE)
    mkdir_p(out_dir)
    with open(out_file, "a") as f:
        for i in range(EPISODE):
            f.write("----- Episode {} -----".format(i))
            for j in range(EPISODE_LENGTH):
                time.sleep(0.5)
                k = 0
                while (not observer.is_in_app()) and k < MAX_STEP_BACK:
                    executor.press_back()
                    k = k + 1
                if not observer.is_in_app():
                    executor.start_activity(PACKAGE, LAUNCHER)
                else:
                    # Step 1. Observe gui state
                    s1 = observer.get_gui_state()[0]
                    # Step 2. Get coverage
                    c1 = float(get_coverage(APP_NAME))
                    # Step 3. Pre-process data
                    x = processor.create_input_matrix_2d(s1)
                    # Step 4. Neural network forward pass
                    a = random.choice(s1)
                    # Step 5. Execute selected action
                    executor.perform_action(a)
                    # Step 6. Observe new state
                    s2 = observer.get_gui_state()[0]
                    # Step 7. Get coverage and calculate reward
                    c2 = float(get_coverage(APP_NAME))
                    r = c2-c1
                    # Step 8. Save transition to replay memory
                    f.write(str((s1, a, r, s2)) + "\n")
                    # Step 9. Gradient update

