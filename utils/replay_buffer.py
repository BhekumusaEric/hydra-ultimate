import random
from collections import deque

class ReplayBuffer:
    def __init__(self, max_size=1000):
        self.buffer = deque(maxlen=max_size)

    def add(self, state, action, reward, next_state):
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size=32):
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))