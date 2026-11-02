"""The TCP retransmission timer from RFC 6298. Chapter 6."""


class RtoEstimator:
    def __init__(self, granularity=0.001, minimum=1.0, maximum=60.0):
        self.granularity, self.minimum, self.maximum = granularity, minimum, maximum
        self.srtt = self.rttvar = None
        self.rto = 1.0  # the initial value, before any measurement

    def sample(self, rtt):
        if self.srtt is None:
            self.srtt, self.rttvar = rtt, rtt / 2
        else:
            self.rttvar = 0.75 * self.rttvar + 0.25 * abs(self.srtt - rtt)  # before srtt changes
            self.srtt = 0.875 * self.srtt + 0.125 * rtt
        self.rto = self._clamp(self.srtt + max(self.granularity, 4 * self.rttvar))
        return self.rto

    def on_timeout(self):
        """The timer fired: back off, doubling."""
        self.rto = self._clamp(self.rto * 2)
        return self.rto

    def _clamp(self, rto):
        return min(self.maximum, max(self.minimum, rto))
