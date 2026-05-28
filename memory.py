from collections import deque
from datetime import datetime

class ConversationMemory:
    def __init__(self, max_history=20):
        self.history = deque(maxlen=max_history)
        self.context = {}          # stores key facts (e.g. user name)
        self.session_start = datetime.now()

    def add(self, role: str, message: str, intent: str = None):
        self.history.append({
            "role": role,           # "user" or "bot"
            "message": message,
            "intent": intent,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(self):
        return list(self.history)

    def get_last_intent(self):
        for entry in reversed(self.history):
            if entry["role"] == "user" and entry.get("intent"):
                return entry["intent"]
        return None

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)

    def clear(self):
        self.history.clear()
        self.context.clear()