import tensorflow as tf
import numpy as np

def exponential_decay(step, total, initial, final, rate=1e-4, stairs=None):
    if stairs is not None:
        step = stairs * tf.floor(step / stairs)
    scale, offset = 1. / (1. - rate), 1. - (1. / (1. - rate))
    progress = tf.cast(step, tf.float32) / tf.cast(total, tf.float32)
    value = (initial - final) * scale * rate ** progress + offset + final
    lower, upper = tf.minimum(initial, final), tf.maximum(initial, final)
    return tf.maximum(lower, tf.minimum(value, upper))


def _qvalues(observ):
    with tf.variable_scope('qvalues', reuse=True):
        # Network from DQN (Mnih 2015)
        h1 = tf.layers.conv2d(observ, 32, 8, 4, tf.nn.relu)
        h2 = tf.layers.conv2d(h1, 64, 4, 2, tf.nn.relu)
        h3 = tf.layers.conv2d(h2, 64, 3, 1, tf.nn.relu)
        h4 = tf.layers.dense(h3, 512, tf.nn.relu)
        return tf.layers.dense(h4, num_actions, None)

# target network
def bind(output, inputs):
    for key in inputs:
        if isinstance(inputs[key], tf.Variable):
            inputs[key] = inputs[key].value()
    return tf.contrib.graph_editor.graph_replace(output, inputs)

def moving_average(output, decay=0.999, collection=tf.GraphKeys.TRAINABLE_VARIABLES):
    average = tf.train.ExponentialMovingAverage(decay=decay)
    variables = set(v.value() for v in output.graph.get_collection(collection))
    deps = tf.contrib.graph_editor.get_backward_walk_ops(output)
    deps = [t for o in deps for t in o.values()]
    deps = set([t for t in deps if t in variables])
    update_op = average.apply(deps)
    new_output = bind(output, {t: average.average(t) for t in deps})
    return new_output, update_op


current = tf.gather(_qvalues(observ), action)[:, 0]
target_qvalues = moving_average(_qvalues(nextob), 0.999)
target = reward + gamma * tf.reduce_max(target_qvalues, 1)
target = tf.where(done, tf.zeros_like(target), target)
loss = (current - target) ** 2

step = 10000
num_actions = 5



epsilon = exponential_decay(step, 50000, 1.0, 0.05, rate=0.5)
best_action = tf.arg_max(_qvalues([observ])[0], 0)
random_action = tf.random_uniform((), 0, num_actions, tf.int64)
should_explore = tf.random_uniform((), 0, 1) < epsilon
tf.cond(should_explore, lambda: random_action, lambda: best_action)
