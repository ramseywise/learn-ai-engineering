"""The TCP retransmission timer from RFC 6298. Chapter 6.

Read section 2 of the RFC: https://www.rfc-editor.org/rfc/rfc6298
"""


class RtoEstimator:
    def __init__(self, granularity=0.001, minimum=1.0, maximum=60.0):
        self.granularity, self.minimum, self.maximum = granularity, minimum, maximum
        self.srtt = self.rttvar = None
        self.rto = 1.0

    def sample(self, rtt):
        """Take one round-trip measurement, in seconds, and return the new RTO."""
        raise NotImplementedError

    def on_timeout(self):
        """The timer fired. Back off, and return the new RTO."""
        raise NotImplementedError
