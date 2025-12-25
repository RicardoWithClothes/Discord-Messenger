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
    qt_start: str = None 
    qt_end: str = None
    tasks: list[Task] = field(default_factory=list)

    def __str__(self) -> str:
        qt_stat = "(QT ON)" if self.qt_start and self.qt_end else ""
        return f"{self.username} {qt_stat}"
    
    def isQuietTime(self, checkTime: datetime.datetime) -> bool:
        """Checks if the given time is within the quiet time."""
        if self.qt_start < self.qt_end:
            return self.qt_start <= checkTime <= self.qt_end
        else:
            return checkTime >= self.qtimeStart or checkTime <= self.qtimeEnd
    def setQuietTime(self, start: datetime.datetime, end: datetime.datetime):
        """Sets the quiet time for the resipient."""
        self.qtimeStart = start
        self.qtimeEnd = end