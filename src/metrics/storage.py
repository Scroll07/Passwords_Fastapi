from collections import defaultdict

class MetricsStorage:
    def __init__(self) -> None:
        self.count_requests = defaultdict(int)
        self.active_requests = defaultdict(int)
        self.duration = defaultdict(list)

metrics = MetricsStorage()