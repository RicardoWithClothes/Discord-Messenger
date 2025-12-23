import uuid
import datetime
from dataclasses import dataclass, field

@dataclass
class Task:
    """Stores the data for the task."""
    channel_id: int
    message: str
    run_time: datetime.datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: str = "Pending"

    def __str__(self) -> str:
        time_str = self.run_time.strftime("%H:%M:%S")
        return f"[{time_str}] ID:{self.channel_id} - {self.status}"
    

@dataclass    
class SavedContact: 
    """Stores the data for the saved contact."""
    channel_id: int
    username: str

    # qtimeStart: datetime.datetime
    # qtimeEnd: datetime.datetime
    tasks: list[Task] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.username}"
    
    # def isQuietTime(self, checkTime: datetime.datetime) -> bool:
        """Checks if the given time is within the quiet time."""
        if self.qtimeStart < self.qtimeEnd:
            return self.qtimeStart <= checkTime <= self.qtimeEnd
        else:
            return checkTime >= self.qtimeStart or checkTime <= self.qtimeEnd
    # def setQuietTime(self, start: datetime.datetime, end: datetime.datetime):
        """Sets the quiet time for the resipient."""
        self.qtimeStart = start
        self.qtimeEnd = end