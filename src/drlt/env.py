import random
import time
import logging
import subprocess
from .device.device import DeviceApp

"""
State is a tuple (activity_name, tuple of actions)
action is a tuple (resource_id, event_type, bounds, text or "")
"""

#TOD0 handle out of app

DEFAULT_REWARD = 0
RECORDA_WEIGHT = 10
MAX_CLICK = 2

logger = logging.getLogger(__name__)

class Environment(object):

    def __init__(self, device_name, package, config):
        self.device = DeviceApp(device_name, package)
        self.package = package
        self.config = config

        self._screen = None
        self.reward = 0
        self.terminal = True

        self.next_state = None
        self.current_state = None
        self.visited_states = None

    def observe_current_state(self):
        self.device.observer.dump_gui()
        state = (self.device.observer.activity, self.device.observer.app_actions)
        return state

    def transition_to_next_state(self, action):
        if not action:
            # No action to select
            self.device.press.back()
        else:
            self.device.executor.perform_action(action)
        time.sleep(0.2)
        next_state = self.observe_current_state()
        # Check if next state is out of app
        if self.is_out_of_app(next_state[0]):
            self.handle_out_of_app(MAX_CLICK)
            self.next_state = None
            self.current_state = self.observe_current_state()
            return None
        elif "Application Error" in next_state[0]:
            self.kill_app()
            return None
        self.next_state = next_state
        # If next state is out of app, return None
        return next_state

    def set_current_state(self):
        self.current_state = self.observe_current_state()

    def finish_transition(self):
        if self.next_state in self.visited_states:
            self.visited_states[self.next_state] += 1
        else:
            self.visited_states[self.next_state] = 1
        self.current_state = self.next_state
        self.next_state = None

    def get_count_reward(self):
        if self.next_state in self.visited_states and self.visited_states[self.next_state] != 0:
            # logger.info("Count reward {}".format(1/float(self.visited_states[self.next_state])))
            return 1/float(self.visited_states[self.next_state])
        return 0

    def get_gui_change_reward(self):
        reward = 0
        if self.next_state and self.current_state:
            current_actions = self.current_state[1]
            next_actions = self.next_state[1]
            if len(next_actions) != 0:
                # If next state has no action, return reward 0
                shared_items = set(current_actions) & set(next_actions)
                reward = (len(next_actions) - len(shared_items))/float(len(next_actions))
        # logger.info("GUI reward {}".format(reward))
        return reward

    def get_reward(self, action):
        reward = self.get_gui_change_reward() + self.get_count_reward()
        return reward

    def get_random_state(self):
        return random.choice(self.visited_states.keys())[0]

    def is_out_of_app(self, activity):
        """Check is out of app."""
        if self.package in activity:
            return False
        else:
            return True

    def back_to_app(self):
        logger.info('backtoapp')
        subprocess.call(['adb', 'shell', 'monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])

    def jump_to_activity(self, activity):
        output = subprocess.check_output(['adb', 'shell', 'am', 'start', '-n', '{}/{}'.format(self.package, activity)])
        logger.info("Jump to activity {} : {}".format(activity, output))
        return output

    def kill_app(self):
        output = subprocess.check_output(['adb', 'shell', 'am', 'force-stop', self.package])
        logger.info("Kill app: {}".format(output))

    def handle_out_of_app(self, max_click):
        """
        if out of app, click maximum max_click time, then check if we're back to the app (in case of error)
        if always out of app, back to launcher
        if still out of app, restart the app
        """
        if len(self.device.observer.actionable_events) == 0:
            self.back_to_app()
        else:
            for i in range(max_click):
                random_action = random.choice(self.device.observer.actionable_events)
                self.device.executor.perform_action(random_action)
                if self.device.info['currentPackageName'] == self.package:
                    break

        if self.device.info['currentPackageName'] != self.package:
            self.back_to_app()


import gym
import random
import numpy as np
from .utils import rgb2gray, imresize

class EnvironmentBis(object):
  def __init__(self, config):
    self.env = gym.make(config.env_name)

    screen_width, screen_height, self.action_repeat, self.random_start = \
        config.screen_width, config.screen_height, config.action_repeat, config.random_start

    self.display = config.display
    self.dims = (screen_width, screen_height)

    self._screen = None
    self.reward = 0
    self.terminal = True

  def new_game(self, from_random_game=False):
    if self.lives == 0:
      self._screen = self.env.reset()
    self._step(0)
    self.render()
    return self.screen, 0, 0, self.terminal

  def new_random_game(self):
    self.new_game(True)
    for _ in xrange(random.randint(0, self.random_start - 1)):
      self._step(0)
    self.render()
    return self.screen, 0, 0, self.terminal

  def _step(self, action):
    self._screen, self.reward, self.terminal, _ = self.env.step(action)

  def _random_step(self):
    action = self.env.action_space.sample()
    self._step(action)

  @ property
  def screen(self):
    return imresize(rgb2gray(self._screen)/255., self.dims)
    #return cv2.resize(cv2.cvtColor(self._screen, cv2.COLOR_BGR2YCR_CB)/255., self.dims)[:,:,0]

  @property
  def action_size(self):
    return self.env.action_space.n

  @property
  def lives(self):
    return self.env.ale.lives()

  @property
  def state(self):
    return self.screen, self.reward, self.terminal

  def render(self):
    if self.display:
      self.env.render()

  def after_act(self, action):
    self.render()

class GymEnvironment(Environment):
  def __init__(self, config):
    super(GymEnvironment, self).__init__(config)

  def act(self, action, is_training=True):
    cumulated_reward = 0
    start_lives = self.lives

    for _ in xrange(self.action_repeat):
      self._step(action)
      cumulated_reward = cumulated_reward + self.reward

      if is_training and start_lives > self.lives:
        cumulated_reward -= 1
        self.terminal = True

      if self.terminal:
        break

    self.reward = cumulated_reward

    self.after_act(action)
    return self.state

class SimpleGymEnvironment(Environment):
  def __init__(self, config):
    super(SimpleGymEnvironment, self).__init__(config)

  def act(self, action, is_training=True):
    self._step(action)

    self.after_act(action)
    return self.state


