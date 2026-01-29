import time

class Storage:
    def __init__(self):
        self.channels = {}  # @channel: expire_ts or None
        self.bot_msg_ttl = 30  # seconds

    def add_channel(self, channel):
        self.channels[channel] = None

    def remove_channel(self, channel):
        return self.channels.pop(channel, None)

    def set_channel_timer(self, channel, seconds):
        if channel in self.channels:
            self.channels[channel] = time.time() + seconds
            return True
        return False

    def get_active_channels(self):
        now = time.time()
        to_delete = []
        result = []

        for ch, expire in self.channels.items():
            if expire and expire < now:
                to_delete.append(ch)
            else:
                result.append(ch)

        for ch in to_delete:
            del self.channels[ch]

        return result

storage = Storage()


