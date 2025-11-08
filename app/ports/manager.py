from abc import ABC, abstractmethod
from app.domain import dtos


class Manager(ABC):
    """Manager interface"""

    @abstractmethod
    def summarize(
        self,
        text: dtos.Transcript,
    ) -> dtos.LLMResponse | None:
        pass

    @abstractmethod
    async def asummarize(
        self,
        documents: dtos.Transcripts,
    ) -> dtos.LLMresponses | None:
        pass
