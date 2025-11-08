import asyncio

from app.ports import llm, manager
from app.domain import dtos
from app.domain import prompts
from app.adapters import db
from app import logger


class Controller(manager.Manager):
    """Controller class."""

    def __init__(
        self,
        llm_client: llm.LLm,
    ):
        self._llm_client = llm_client

    def summarize(
        self,
        text: dtos.Transcript,
    ) -> dtos.LLMResponseId | None:
        user_prompt = prompts.RAW_USER_PROMPT.format(
            transcript=text,
        )
        summary = self._llm_client.run_completion(
            system_prompt=prompts.SYSTEM_PROMPT,
            user_prompt=user_prompt,
            dto=dtos.LLMResponse,
        )
        if not summary:
            return None
        response = db.database.create(summary.model_dump())
        return dtos.LLMResponseId.model_validate(response)

    async def asummarize(
        self,
        documents: dtos.Transcripts,
    ) -> dtos.LLMresponses | None:
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
        except Exception as e:  # pylint: disable=broad-except  # multiple things can go wrong here
            logger.exception(e)
            return None

        results = []
        for task in tasks:
            r = task.result()
            if r:
                results.append(r.model_dump())

        return dtos.LLMresponses.model_validate({"responses": await db.database.bulk_acreate(results)})

    def get_summary(self, id: str):  # pylint: disable=redefined-builtin
        return dtos.LLMResponseId.model_validate(db.database.get(id))
