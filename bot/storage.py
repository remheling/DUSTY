class Storage:
    def __init__(self):
        self.channels: set[str] = set()

    def add_channel(self, channel: str):
        self.channels.add(channel.lstrip("@"))

    def remove_channel(self, channel: str) -> bool:
        return self.channels.discard(channel.lstrip("@")) is None

    def clear(self):
        self.channels.clear()

    def get_all(self) -> list[str]:
        return list(self.channels)


storage = Storage()

