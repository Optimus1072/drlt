from observer import observer
from executor import executor
from executor.executor import get_bound_from_string
from config import DEVICE
from uiautomator import Device

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt



def get_index_from_bounds(bounds, step_width, step_height):
    left_index = int(bounds[0] / step_width)
    right_index = int(bounds[1] / step_width)
    top_index = int(bounds[2] / step_height)
    bottom_index = int(bounds[3] / step_height)
    return top_index, bottom_index, left_index, right_index


if __name__ == "__main__":
    # TODO check if device is connected
    device = Device(DEVICE)
    observer = observer.Observer(device)
    executor = executor.Executor(device)
    gui = observer.get_gui_state()[0]
    print(gui)

    INPUT_SIZE = (1500, 1000)
    device_info = device.info
    phone_size = (device_info["displayHeight"], device_info["displayWidth"])
    step_height = phone_size[0] / INPUT_SIZE[0]
    step_width = phone_size[1]/INPUT_SIZE[1]
    print(phone_size)
    x = np.zeros(INPUT_SIZE)
    for component in gui:
        bounds = get_bound_from_string(component[2])
        top_index, bottom_index, left_index, right_index = get_index_from_bounds(bounds, step_width, step_height)
        print(top_index, bottom_index, left_index, right_index)
        x[top_index:bottom_index + 1, left_index:right_index + 1] = x[top_index:bottom_index+1, left_index:right_index+1] +1

    # plt.gray()
    plt.imshow(np.uint8(x))
    plt.show()

