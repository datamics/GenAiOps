from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
try:
    from backend.main import answer_query
    from backend.langfuse_config import setup_telemetry
except ModuleNotFoundError:
    from main import answer_query
    from langfuse_config import setup_telemetry
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import observe

# Init Langfuse Client
langfuse = setup_telemetry()

# Initialize FastAPI app
app = FastAPI(title="Smart Assistant API")

# Add CORS-Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", "")
        )


class ChatRequest(BaseModel):
    message: str
    chat_history: List[ChatMessage] = []


# REST-Endpoint
@app.post("/chat")
@observe(name="chat-endpoint")
async def chat(request: ChatRequest):
    try:
        # Convert Chat-History
        history = []
        for msg in request.chat_history:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
            else:
                role = msg.role
                content = msg.content

            if role == "user":
                history.append(HumanMessage(content=content))
            elif role == "assistant":
                history.append(AIMessage(content=content))

        # Langfuse:
        with langfuse.start_as_current_generation(
            name="answer_query",
            model="gemini-2.5-flash",
            input=request.message,
        ) as generation:
            full_response = answer_query(request.message, history)
            generation.update(output=full_response)

        print(f"Full Answer: {full_response}")

        if not full_response:
            return {"response": "Sorry, I was not able to generate an answer."}

        return {"response": full_response}
    except Exception as e:
        print(f"Error in the Chat-API: {str(e)}")
        import traceback
        print(f"Stacktrace: {traceback.format_exc()}")
        return {
            "response": f"A error occurred: {str(e)}"
        }
