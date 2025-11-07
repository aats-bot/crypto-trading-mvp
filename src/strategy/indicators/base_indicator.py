class BaseIndicator:
    def __init__(self, period: int = 14):
        self.period = int(period)
        self.data = []

    def add_data(self, value: float):
        self.data.append(float(value))

    def get_data(self, n: int = None):
        if n is None:
            return list(self.data)
        return list(self.data[-n:])

    @property
    def is_ready(self) -> bool:
        return len(self.data) >= self.period
