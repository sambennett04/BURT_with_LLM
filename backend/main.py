import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from generate_br import generateReport
from dotenv import load_dotenv

MODEL = "o4-mini-2025-04-16"
MAX_COMPLETION_TOKENS = 32_000
load_dotenv()

class Message(BaseModel):
    sender: str
    text: str

class Messages(BaseModel):
    messages: List[Message]

class Report(BaseModel):
    body: str

app = FastAPI()

origins = [
    "http://localhost:5173",
]

#CORS middleware stops unauthorized calls to api
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generateReport", response_model=Report)
def generate_report(messages : Messages):
    app = messages.messages[0].text
    user_description = messages.messages[1].text
    report = generateReport(app, user_description, MODEL, MAX_COMPLETION_TOKENS)
    return Report(body=report)


if (__name__ == "__main__"):
    uvicorn.run(app, host="0.0.0.0", port=8000)