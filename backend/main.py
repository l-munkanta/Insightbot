from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent import chat

app = FastAPI(title="InsightBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    messages: list

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        reply = chat(req.messages)
        return ChatResponse(reply=reply)
    except Exception as e:
        return ChatResponse(reply=f"Something went wrong: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}