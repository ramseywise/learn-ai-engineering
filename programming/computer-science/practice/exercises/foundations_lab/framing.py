"""Length-prefixed messages over a byte stream. Chapter 6.

A frame is a 4-byte big-endian length followed by that many bytes.
"""


def encode_frame(payload, max_size=1 << 20):
    """Raise ValueError if the payload is larger than max_size."""
    raise NotImplementedError


class FrameDecoder:
    """Feed it bytes as they arrive, cut anywhere. It returns the messages that are complete."""

    def __init__(self, max_size=1 << 20):
        self.max_size = max_size

    def feed(self, data):
        """Returns a list of complete payloads. Raise ValueError on a length over max_size."""
        raise NotImplementedError

    @property
    def pending(self):
        """Bytes held back, waiting for the rest of a frame."""
        raise NotImplementedError
