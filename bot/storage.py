import time

class Storage:
    def __init__(self):
        self.channels = {}  # channel -> expire_ts | None
        self.bot_msg_ttl = 30

    def add_channel(self, channel: str, ttl: int | None = None):
        expire = time.time() + ttl if ttl else None
        self.channels[channel] = expire

    def remove_channel(self, channel: str):
        self.channels.pop(channel, None)

    def cleanup(self):
        now = time.time()
        for ch, exp in list(self.channels.items()):
            if exp and exp <= now:
                del self.channels[ch]

    def get_channels(self):
        self.cleanup()
        return list(self.channels.keys())


storage = Storage()


