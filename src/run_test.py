from observer import observer
from executor import executor
from config import *
from uiautomator import Device

if __name__ == "__main__":
    # TODO check if device is connected
    device = Device(DEVICE)
    observer = observer.Observer(device)
    executor = executor.Executor(device)
    state = observer.get_current_state()
    print state[0][10]
    executor.perform_action(state[0][0])
