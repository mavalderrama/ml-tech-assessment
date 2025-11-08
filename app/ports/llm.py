from abc import ABC, abstractmethod
import pydantic


class LLm(ABC):
    """LLM interface"""

    @abstractmethod
    def run_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        dto: type[pydantic.BaseModel],
    ) -> pydantic.BaseModel | None:
        pass

    @abstractmethod
    async def run_completion_async(
        self,
        system_prompt: str,
        user_prompt: str,
        dto: type[pydantic.BaseModel],
    ) -> pydantic.BaseModel | None:
        pass
