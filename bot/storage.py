# storage.py

class ChannelStorage:
    def __init__(self):
        self._channels: list[str] = []

    def add_channel(self, username: str):
        username = username.lower()
        if username not in self._channels:
            self._channels.append(username)

    def remove_channel(self, username: str) -> bool:
        username = username.lower()
        if username in self._channels:
            self._channels.remove(username)
            return True
        return False

    def clear_channels(self):
        self._channels.clear()

    def get_channels(self) -> list[str]:
        return self._channels.copy()


storage = ChannelStorage()

