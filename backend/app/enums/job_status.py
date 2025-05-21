from enum import Enum

class JobStatus(Enum):
    FAILED = "failed"
    PROCESSING = "processing"
    COMPLETED = "completed"