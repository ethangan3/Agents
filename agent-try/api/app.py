from fastapi import FastAPI, HTTPException
from .schema import AskRequest, AskResponse, HistoryItem
from service .qa_service import ask_agent
from pathlib import Path
from dotenv import load_dotenv
import os

app = FastAPI(
    title="QA Assist API",
    version="0.1.0",
    description="基于 ReActAgent 的问答接口",
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        response = ask_agent(request.question, save_flag=request.save_flag)
        return AskResponse(
            question=response.question,
            answer=response.answer,
            reasoning=response.reason
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))