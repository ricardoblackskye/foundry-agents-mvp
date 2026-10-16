import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="Foundry Hosted Agent",
    description="Azure AI Foundry hosted agent implementing the responses protocol",
    version="0.1.0"
)

class Message(BaseModel):
    role: str
    content: str

class ResponsesRequest(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    temperature: Optional[float] = 0.7

class ResponseContent(BaseModel):
    role: str = "assistant"
    content: str

class ResponsesResponse(BaseModel):
    response: ResponseContent
    protocol: str = "responses"

@app.get("/readiness")
async def readiness():
    """Foundry health probe endpoint."""
    return {"status": "ready"}

@app.post("/responses", response_model=ResponsesResponse)
async def handle_responses(request: ResponsesRequest):
    """Foundry responses protocol conversational handler."""
    if not request.messages:
        return JSONResponse(
            status_code=400,
            content={"error": "The 'messages' list cannot be empty."}
        )

    last_user_message = request.messages[-1].content
    reply_text = f"Foundry Agent received: {last_user_message}"

    return ResponsesResponse(
        response=ResponseContent(role="assistant", content=reply_text),
        protocol="responses"
    )

def start():
    port = int(os.environ.get("PORT", 8088))
    uvicorn.run("src.agent.main:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start()
