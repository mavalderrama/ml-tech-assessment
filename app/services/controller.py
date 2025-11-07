import pydantic

from app.ports import llm, manager
from app.domain import dtos
from app.domain import prompts
import asyncio
from logger import logger
from app.adapters import db


class Controller(manager.Manager):
    def __init__(
        self,
        llm_client: llm.LLm,
    ):
        self._llm_client = llm_client

    def summarize(
        self,
        text: dtos.Transcript,
    ) -> pydantic.BaseModel:
        user_prompt = prompts.RAW_USER_PROMPT.format(
            transcript=text,
        )
        summary = self._llm_client.run_completion(
            system_prompt=prompts.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            dto=dtos.LLMResponse,
        )
        response = db.database.create(summary.model_dump())
        return dtos.LLMResponseId.model_validate(response)

    async def asummarize(
        self,
        documents: dtos.Transcripts,
    ) -> dtos.LLMresponses:
        system_prompt = prompts.SYSTEM_PROMPT
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = []
                for text in documents.transcripts:
                    user_prompt = prompts.RAW_USER_PROMPT.format(
                        transcript=text,
                    )

                    tasks.append(
                        tg.create_task(
                            self._llm_client.run_completion_async(
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                dto=dtos.LLMResponse,
                            )
                        )
                    )
        except Exception as e:
            logger.exception(e)

        results = []
        for task in tasks:
            r = task.result()
            results.append(r.model_dump())

        return dtos.LLMresponses(responses=await db.database.bulk_acreate(results))

    def get_summary(self, id: str):
        return dtos.LLMResponseId.model_validate(db.database.get(id))
