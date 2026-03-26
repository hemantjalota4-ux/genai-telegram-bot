from collections import defaultdict, deque

class Memory:
    def __init__(self, k=3):
        self.data = defaultdict(lambda: deque(maxlen=k))

    def add(self, user_id, message):
        self.data[user_id].append(message)

    def get(self, user_id):
        return list(self.data[user_id])


memory = Memory(k=3)