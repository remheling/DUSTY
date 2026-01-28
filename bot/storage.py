class Storage:
    def __init__(self):
        self.channels: list[str] = []

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

    def get_channels(self) -> list[str]:
        return self.channels.copy()

    def has_channels(self) -> bool:
        return len(self.channels) > 0


storage = Storage()

