class Storage:
    def __init__(self):
        self.channels: list[str] = []
        self.delete_timer: int = 60

    def set_channels(self, channels: list[str]):
        self.channels = channels

    def add_channel(self, channel: str):
        if channel not in self.channels:
            self.channels.append(channel)

    def remove_channel(self, channel: str) -> bool:
        if channel in self.channels:
            self.channels.remove(channel)
            return True
        return False

    def clear_channels(self):
        self.channels.clear()

    def get_channels(self):
        return self.channels

    def set_timer(self, seconds: int):
        self.delete_timer = seconds

    def get_timer(self):
        return self.delete_timer


storage = Storage()
