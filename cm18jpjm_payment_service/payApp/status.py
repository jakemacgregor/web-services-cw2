from enum import Enum


class Status(Enum):
    ORDER_CREATED = 0
    PENDING = 1
    SUCCESSFUL = 2
    FAILED = 3
    CANCELLED = 4
