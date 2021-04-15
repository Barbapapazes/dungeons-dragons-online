import heapq


class PriorityQueue:
    """Queue with priority, lower priority is the first return, implemented as (priority, data)"""

    def __init__(self):
        self.content = []

    def isEmpty(self):
        return (len(self.content) == 0)

    def push(self, item, priority):
        """Push an item on the heap, depending on the priority"""
        heapq.heappush(self.content, (priority, item))

    def pop(self):
        """Return value of the lowest priority"""
        _, value = heapq.heappop(self.content)
        return value
