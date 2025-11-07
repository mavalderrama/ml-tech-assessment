from abc import ABC, abstractmethod
from app.domain import dtos


class Manager(ABC):
    @abstractmethod
    def summarize(self, text: dtos.Transcript):
        pass

    @abstractmethod
    async def asummarize(self, text: dtos.Transcripts):
        pass
