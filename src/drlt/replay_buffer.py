import tensorflow as tf


class ReplayBuffer(object):
    def __init__(self, template, capacity):
        self._capacity = capacity
        self._buffers = self._create_buffers(template)
        self._index = tf.Variable(0, dtype=tf.int32, trainable=False)

    def size(self):
        return tf.minimum(self._index, self._capacity)

    def _create_buffers(self, template):
        buffers = []
        for tensor in template:
            shape = tf.TensorShape([self._capacity]).concatenate(tensor.get_shape())
            initial = tf.zeros(shape, tensor.dtype)
            buffers.append(tf.Variable(initial, trainable=False))
        return buffers

    def append(self, tensors):
        position = tf.mod(
            self._index, self._capacity)
        with tf.control_dependencies([
            b[position].assign(t) for b, t in
            zip(self._buffers, tensors)]):
            return self._index.assign_add(1)

    def sample(self, amount):
        positions = tf.random_uniform((amount,), 0, self.size - 1, tf.int32)
        return [tf.gather(b, positions) for b in self._buffers]


class PrioritizedReplayBuffer:
    def __init__(self, template, capacity):
        template = (tf.constant(0.0),) + tuple(template)
        self._buffer = ReplayBuffer(template, capacity)

    def size(self):
        return self._buffer.size

    def append(self, priority, tensors):
        return self._buffer.append((priority,) + tuple(tensors))

    def sample(self, amount, temperature=1):
        priorities = self._buffer._buffers[0].value()[:self._buffer.size()]
        logprobs = tf.log(priorities / tf.reduce_sum(priorities)) / temperature
        positions = tf.multinomial(logprobs[None, ...], amount)[0]
        return [tf.gather(b, positions) for b in self._buffer._buffers[1:]]