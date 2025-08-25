from enum import Enum

class InjuryStatus(str, Enum):
    AVAILABLE = "available"
    DOUBTFUL = "doubtful"
    INJURED = "injured"
    SUSPENDED = "suspended"