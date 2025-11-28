from typing import List
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler
import os
from dotenv import load_dotenv
try:
    from graph import app
except ModuleNotFoundError:
    from backend.graph import app

load_dotenv()

def answer_query(user_query: str, chat_history: List = None) -> str:
    if chat_history is None:
        chat_history = []

    messages = chat_history + [HumanMessage(content=user_query)]

    langfuse_handler = CallbackHandler()

    config = {
        "recursion_limit": 50,
        "callbacks": [langfuse_handler]
    }

    result_state = app.invoke({"messages": messages}, config=config)

    answer = result_state["messages"][-1].content

    # Handle Gemini's grounding signatures (structured content) - appears when the retriever is used.
    if isinstance(answer, list):
        text_parts = []
        for part in answer:
            if isinstance(part, dict) and part.get('type') == 'text':
                text_parts.append(part.get('text', ''))
        answer = ''.join(text_parts)
    return answer


if __name__ == "__main__":
    print(answer_query("What is the weather in Berlin?"))
