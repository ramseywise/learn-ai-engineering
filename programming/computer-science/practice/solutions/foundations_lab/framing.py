"""Length-prefixed messages over a byte stream. Chapter 6."""

import struct

HEADER = struct.Struct(">I")


def encode_frame(payload, max_size=1 << 20):
    if len(payload) > max_size:
        raise ValueError("frame too large")
    return HEADER.pack(len(payload)) + payload


class FrameDecoder:
    """Feed it bytes as they arrive, cut anywhere. It returns the messages that are complete."""

    def __init__(self, max_size=1 << 20):
        self.max_size = max_size
        self._buffer = bytearray()

    def feed(self, data):
        self._buffer += data
        frames = []
        while len(self._buffer) >= HEADER.size:
            length = HEADER.unpack_from(self._buffer)[0]
            if length > self.max_size:  # check before buffering: the sender doesn't get to choose
                raise ValueError("frame too large")
            end = HEADER.size + length
            if len(self._buffer) < end:
                break
            frames.append(bytes(self._buffer[HEADER.size:end]))
            del self._buffer[:end]
        return frames

    @property
    def pending(self):
        return len(self._buffer)
