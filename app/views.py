from typing import Annotated
from fastapi import FastAPI, HTTPException, Body
from app.domain import dtos, configurations
from app.services import controller
from app.adapters import openai


from app import logger

app = FastAPI()

master_control = controller.Controller(
    llm_client=openai.OpenAIAdapter(
        configurations.app_settings.OPENAI_API_KEY,
        configurations.app_settings.OPENAI_MODEL,
    ),
)


@app.get("/")
async def root():
    return {"message": "Hello AceUp"}


@app.get("/summary")
def get_summary(id: str) -> dtos.LLMResponseId:  # pylint: disable=redefined-builtin
    if not (result := master_control.get_summary(id=id)):
        raise HTTPException(status_code=404, detail="Summary not found")
    return result


@app.post("/summary/generate")
def summarize(
    text: Annotated[
        dtos.Transcript,
        Body(
            examples=[
                {
                    "text": "Mark Foster | MCC, ACTC: Hey there, Liam. Glad we could find a few minutes for this one-on-one. How are things going?\nLiam Garcia: Hey, Mark. Doing well, thanks. It’s been a busy week—my local dev environment is a bit cluttered from a new feature branch, but I’m making progress. Ready to dig in on Python best practices?\nMark Foster | MCC, ACTC: Absolutely. I know you wanted to focus on a handful of coding guidelines and how they tie into your team’s speed. Let’s start big picture: what’s motivating you to tighten up your Python practices right now?\nLiam Garcia: Mainly two reasons. First, the codebase is growing, and I want to make sure we’re consistent in how we name things, structure modules, and write docstrings. Second, I’m onboarding new developers, and I’ve noticed they can get lost if we don’t have explicit standards in place.\nMark Foster | MCC, ACTC: Makes sense. So, if we look at code readability—PEP 8, docstrings, that sort of thing—what’s your first priority?\nLiam Garcia: Definitely PEP 8. That’s sort of non-negotiable. I’d like us to adopt a tool like Black to auto-format. That alone can reduce the back-and-forth on code reviews. It’s a small step but a huge time-saver.\nMark Foster | MCC, ACTC: I love it. Automating style enforcement frees you up to focus on more important stuff—like logic, architecture, and performance. Any concerns about pushback from your devs?\nLiam Garcia: A bit. Some folks are used to their own formatting quirks. But I keep reminding them it’s not about personal style—it’s about consistent style that benefits everyone. I think once they see the time saved, they’ll be on board.\nMark Foster | MCC, ACTC: Good call. How about docstrings? I know some devs skip them unless forced.\nLiam Garcia: Right. I’m pushing for Google-style docstrings. For classes, methods, and modules, they clarify purpose and expected inputs/outputs. It’s a bit of extra effort at first, but it pays off when you come back months later or when a new dev jumps in.\nMark Foster | MCC, ACTC: So your plan is PEP 8 plus auto-formatting, then Google-style docstrings. Anything else on your radar?\nLiam Garcia: Yes—test coverage. We’re aiming for 80% coverage in the short term. That ensures we catch regressions early. I’m also encouraging test-driven development for bigger features. It’s not mandatory, but I want the team comfortable with writing tests before the code whenever possible.\nMark Foster | MCC, ACTC: Great. You mentioned wanting to go faster as a team. How do you see these coding best practices speeding things up, rather than slowing them down?\nLiam Garcia: Well, the time you invest in writing docstrings or running auto-format tools is minimal compared to the hassle of deciphering unstructured code. It’s like a Formula One pit stop—everyone knows their role, follows the same procedure, and the car is back on track fast. Consistency and clarity remove friction.\nMark Foster | MCC, ACTC: That’s an excellent analogy. So what’s your biggest concern about implementing all this?\nLiam Garcia: Probably that initial pushback, or the fear that it’s “too much process.” But I think if I keep reminding folks it’s about removing headaches—like merges, weird naming conflicts, missing tests—they’ll adopt it.\nMark Foster | MCC, ACTC: It often helps to show quick wins. For instance, once your team sees how auto-formatting catches stray imports or how docstrings make a confusing function crystal clear, they’ll realize it’s worth it.\nLiam Garcia: Exactly. I’ll start small, maybe run a pilot on one module, let them see the difference, and then expand.\nMark Foster | MCC, ACTC: That’s a solid plan, Liam. So to recap, you’re committing to:\nPEP 8 compliance via Black (or a similar auto-formatting tool).\nGoogle-style docstrings for all modules, classes, and major functions.\nA drive toward 80% test coverage, with TDD on key features.\nAnything else?\nLiam Garcia: That’s the core. I might also do a weekly quick code review session—just me and one other developer—so we can keep each other honest on these standards.\nMark Foster | MCC, ACTC: That sounds like a perfect next step. How are you feeling as we wrap up?\nLiam Garcia: Confident. I know it’ll take some nudging, but once everyone sees the impact, I think we’ll be coding cleaner, shipping faster.\nMark Foster | MCC, ACTC: Couldn’t have said it better. Thanks for the update, Liam. I look forward to hearing how it goes once you put these into practice.\nLiam Garcia: Thanks, Mark. I appreciate the guidance and encouragement. We’ll talk again soon—hopefully with good news on the coverage front!\nMark Foster | MCC, ACTC: Sounds like a plan. Take care, Liam."  # pylint: disable=line-too-long
                }
            ]
        ),
    ],
) -> dtos.LLMResponseId:
    logger.info("Processing transcript syncronously: with, %s chars", {len(text.text)})
    if not (summary := master_control.summarize(text=text)):
        raise HTTPException(status_code=404, detail="Invalid summary")
    logger.info("transcript processed")
    return summary


@app.post("/summary/batch_generate")
async def asummarize(
    documents: Annotated[
        dtos.Transcripts,
        Body(
            examples=[
                {
                    "transcripts": [
                        {
                            "text": "Mark Foster | MCC, ACTC: Hey there, Liam. Glad we could find a few minutes for this one-on-one. How are things going?\nLiam Garcia: Hey, Mark. Doing well, thanks. It’s been a busy week—my local dev environment is a bit cluttered from a new feature branch, but I’m making progress. Ready to dig in on Python best practices?\nMark Foster | MCC, ACTC: Absolutely. I know you wanted to focus on a handful of coding guidelines and how they tie into your team’s speed. Let’s start big picture: what’s motivating you to tighten up your Python practices right now?\nLiam Garcia: Mainly two reasons. First, the codebase is growing, and I want to make sure we’re consistent in how we name things, structure modules, and write docstrings. Second, I’m onboarding new developers, and I’ve noticed they can get lost if we don’t have explicit standards in place.\nMark Foster | MCC, ACTC: Makes sense. So, if we look at code readability—PEP 8, docstrings, that sort of thing—what’s your first priority?\nLiam Garcia: Definitely PEP 8. That’s sort of non-negotiable. I’d like us to adopt a tool like Black to auto-format. That alone can reduce the back-and-forth on code reviews. It’s a small step but a huge time-saver.\nMark Foster | MCC, ACTC: I love it. Automating style enforcement frees you up to focus on more important stuff—like logic, architecture, and performance. Any concerns about pushback from your devs?\nLiam Garcia: A bit. Some folks are used to their own formatting quirks. But I keep reminding them it’s not about personal style—it’s about consistent style that benefits everyone. I think once they see the time saved, they’ll be on board.\nMark Foster | MCC, ACTC: Good call. How about docstrings? I know some devs skip them unless forced.\nLiam Garcia: Right. I’m pushing for Google-style docstrings. For classes, methods, and modules, they clarify purpose and expected inputs/outputs. It’s a bit of extra effort at first, but it pays off when you come back months later or when a new dev jumps in.\nMark Foster | MCC, ACTC: So your plan is PEP 8 plus auto-formatting, then Google-style docstrings. Anything else on your radar?\nLiam Garcia: Yes—test coverage. We’re aiming for 80% coverage in the short term. That ensures we catch regressions early. I’m also encouraging test-driven development for bigger features. It’s not mandatory, but I want the team comfortable with writing tests before the code whenever possible.\nMark Foster | MCC, ACTC: Great. You mentioned wanting to go faster as a team. How do you see these coding best practices speeding things up, rather than slowing them down?\nLiam Garcia: Well, the time you invest in writing docstrings or running auto-format tools is minimal compared to the hassle of deciphering unstructured code. It’s like a Formula One pit stop—everyone knows their role, follows the same procedure, and the car is back on track fast. Consistency and clarity remove friction.\nMark Foster | MCC, ACTC: That’s an excellent analogy. So what’s your biggest concern about implementing all this?\nLiam Garcia: Probably that initial pushback, or the fear that it’s “too much process.” But I think if I keep reminding folks it’s about removing headaches—like merges, weird naming conflicts, missing tests—they’ll adopt it.\nMark Foster | MCC, ACTC: It often helps to show quick wins. For instance, once your team sees how auto-formatting catches stray imports or how docstrings make a confusing function crystal clear, they’ll realize it’s worth it.\nLiam Garcia: Exactly. I’ll start small, maybe run a pilot on one module, let them see the difference, and then expand.\nMark Foster | MCC, ACTC: That’s a solid plan, Liam. So to recap, you’re committing to:\nPEP 8 compliance via Black (or a similar auto-formatting tool).\nGoogle-style docstrings for all modules, classes, and major functions.\nA drive toward 80% test coverage, with TDD on key features.\nAnything else?\nLiam Garcia: That’s the core. I might also do a weekly quick code review session—just me and one other developer—so we can keep each other honest on these standards.\nMark Foster | MCC, ACTC: That sounds like a perfect next step. How are you feeling as we wrap up?\nLiam Garcia: Confident. I know it’ll take some nudging, but once everyone sees the impact, I think we’ll be coding cleaner, shipping faster.\nMark Foster | MCC, ACTC: Couldn’t have said it better. Thanks for the update, Liam. I look forward to hearing how it goes once you put these into practice.\nLiam Garcia: Thanks, Mark. I appreciate the guidance and encouragement. We’ll talk again soon—hopefully with good news on the coverage front!\nMark Foster | MCC, ACTC: Sounds like a plan. Take care, Liam."  # pylint: disable=line-too-long
                        },
                        {
                            "text": "Mark Foster | MCC, ACTC: Hey there, Liam. Glad we could find a few minutes for this one-on-one. How are things going?\nLiam Garcia: Hey, Mark. Doing well, thanks. It’s been a busy week—my local dev environment is a bit cluttered from a new feature branch, but I’m making progress. Ready to dig in on Python best practices?\nMark Foster | MCC, ACTC: Absolutely. I know you wanted to focus on a handful of coding guidelines and how they tie into your team’s speed. Let’s start big picture: what’s motivating you to tighten up your Python practices right now?\nLiam Garcia: Mainly two reasons. First, the codebase is growing, and I want to make sure we’re consistent in how we name things, structure modules, and write docstrings. Second, I’m onboarding new developers, and I’ve noticed they can get lost if we don’t have explicit standards in place.\nMark Foster | MCC, ACTC: Makes sense. So, if we look at code readability—PEP 8, docstrings, that sort of thing—what’s your first priority?\nLiam Garcia: Definitely PEP 8. That’s sort of non-negotiable. I’d like us to adopt a tool like Black to auto-format. That alone can reduce the back-and-forth on code reviews. It’s a small step but a huge time-saver.\nMark Foster | MCC, ACTC: I love it. Automating style enforcement frees you up to focus on more important stuff—like logic, architecture, and performance. Any concerns about pushback from your devs?\nLiam Garcia: A bit. Some folks are used to their own formatting quirks. But I keep reminding them it’s not about personal style—it’s about consistent style that benefits everyone. I think once they see the time saved, they’ll be on board.\nMark Foster | MCC, ACTC: Good call. How about docstrings? I know some devs skip them unless forced.\nLiam Garcia: Right. I’m pushing for Google-style docstrings. For classes, methods, and modules, they clarify purpose and expected inputs/outputs. It’s a bit of extra effort at first, but it pays off when you come back months later or when a new dev jumps in.\nMark Foster | MCC, ACTC: So your plan is PEP 8 plus auto-formatting, then Google-style docstrings. Anything else on your radar?\nLiam Garcia: Yes—test coverage. We’re aiming for 80% coverage in the short term. That ensures we catch regressions early. I’m also encouraging test-driven development for bigger features. It’s not mandatory, but I want the team comfortable with writing tests before the code whenever possible.\nMark Foster | MCC, ACTC: Great. You mentioned wanting to go faster as a team. How do you see these coding best practices speeding things up, rather than slowing them down?\nLiam Garcia: Well, the time you invest in writing docstrings or running auto-format tools is minimal compared to the hassle of deciphering unstructured code. It’s like a Formula One pit stop—everyone knows their role, follows the same procedure, and the car is back on track fast. Consistency and clarity remove friction.\nMark Foster | MCC, ACTC: That’s an excellent analogy. So what’s your biggest concern about implementing all this?\nLiam Garcia: Probably that initial pushback, or the fear that it’s “too much process.” But I think if I keep reminding folks it’s about removing headaches—like merges, weird naming conflicts, missing tests—they’ll adopt it.\nMark Foster | MCC, ACTC: It often helps to show quick wins. For instance, once your team sees how auto-formatting catches stray imports or how docstrings make a confusing function crystal clear, they’ll realize it’s worth it.\nLiam Garcia: Exactly. I’ll start small, maybe run a pilot on one module, let them see the difference, and then expand.\nMark Foster | MCC, ACTC: That’s a solid plan, Liam. So to recap, you’re committing to:\nPEP 8 compliance via Black (or a similar auto-formatting tool).\nGoogle-style docstrings for all modules, classes, and major functions.\nA drive toward 80% test coverage, with TDD on key features.\nAnything else?\nLiam Garcia: That’s the core. I might also do a weekly quick code review session—just me and one other developer—so we can keep each other honest on these standards.\nMark Foster | MCC, ACTC: That sounds like a perfect next step. How are you feeling as we wrap up?\nLiam Garcia: Confident. I know it’ll take some nudging, but once everyone sees the impact, I think we’ll be coding cleaner, shipping faster.\nMark Foster | MCC, ACTC: Couldn’t have said it better. Thanks for the update, Liam. I look forward to hearing how it goes once you put these into practice.\nLiam Garcia: Thanks, Mark. I appreciate the guidance and encouragement. We’ll talk again soon—hopefully with good news on the coverage front!\nMark Foster | MCC, ACTC: Sounds like a plan. Take care, Liam."  # pylint: disable=line-too-long
                        },
                    ]
                }
            ]
        ),
    ],
) -> dtos.LLMresponses:
    logger.info(
        "Processing documents asyncrously: with %s documents",
        {len(documents.transcripts)},
    )
    if not (summaries := await master_control.asummarize(documents=documents)):
        raise HTTPException(status_code=404, detail="Invalid summary")
    logger.info("documents processed")
    return summaries


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
