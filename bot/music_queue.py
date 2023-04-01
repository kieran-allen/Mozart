from collections import deque


class MusicQueue:
    def __init__(self):
        self.queue = deque()

    def push_front(self, item):
        self.queue.appendleft(item)

    def push_back(self, item):
        self.queue.append(item)

    def pop_front(self):
        return self.queue.popleft()

    def clear(self):
        self.queue.clear()

    def is_empty(self):
        return len(self.queue) == 0
