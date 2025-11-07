from fastapi import FastAPI
from app.domain import dtos
from app.services import controller
from app.adapters import openai
from configurations import app_settings
from logger import logger

app = FastAPI()

master_control = controller.Controller(
    llm_client=openai.OpenAIAdapter(
        app_settings.OPENAI_API_KEY,
        app_settings.OPENAI_MODEL,
    ),
)


@app.get("/")
async def root():
    return {"message": "Hello AceUp"}


@app.get("/summary")
def get_summary(id: str) -> dtos.LLMResponseId:
    return master_control.get_summary(id=id)


@app.post("/summary/generate")
def summarize(text: dtos.Transcript) -> dtos.LLMResponseId:
    logger.info(f"Processing transcript syncronously: {text}")
    summary = master_control.summarize(text=text)
    logger.info("transcript processed")
    return summary


@app.post("/summary/batch_generate")
async def asummarize(documents: dtos.Transcripts) -> dtos.LLMresponses:
    logger.info(f"Processing documents asyncrously: {documents}")
    summaries = await master_control.asummarize(documents=documents)
    logger.info("documents processed")
    return summaries


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
