#%%
#We will implement qdrant Retriever and Weather API as Tools
from backend.agents import get_weather_from_city_name, get_weather_forecast_from_city_name, get_weather_forecast_from_city_name_date_phrase
#%%
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.tools import Tool
from langchain_core.tools.retriever import create_retriever_tool

from langfuse.langchain import CallbackHandler

import sys
import os
import json
from dotenv import load_dotenv
from typing import List
import uvicorn
#%%
load_dotenv()
#%%
SYSTEM_PROMPT = """
You are a helpful assistant. Your purpose is to answer questions regarding the weather and internal documents.

You have the following tools:
- "get_weather_from_city_name": Get the current weather for a given city and country.
- "get_weather_forecast_from_city_name": Get the weather forecast for a given city and country.
- "get_weather_forecast_from_city_name_date_phrase": Get the weather forecast for a given city and country based on a natural language date phrase.
- "Retriever": Access the internal documents.

Always search the internal documents first before using your internal knowledge.
When the user asks for weather, you MUST use the "get_weather_from_city_name" tool. Do not rely on your own knowledge.
When the user asks for weather forecast, you MUST use the "get_weather_forecast_from_city_name" tool. Do not rely on your own knowledge.
If the user is using a relative phrase like "tomorrow", "next Friday", "next week", etc., use the "get_weather_forecast_from_city_name_date_phrase" tool.
When the user asks for other questions, you should use the "Retriever" tool.
"""
#%%
#Set up LLM
google_api_key = os.environ.get("LLM_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    streaming=True,
    google_api_key=google_api_key,
    convert_system_message_to_human=True
)
#%%
#Set up qdrant retriever
def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    qdrant_port = int(os.environ.get("qdrant_port", "6333"))
    client = QdrantClient(os.environ.get("qdrant"), port=qdrant_port)

    vector_db = QdrantVectorStore(
        client=client,
        collection_name=os.environ.get("qdrant_collection"),
        embedding=embeddings,
        content_payload_key="text",
        metadata_payload_key="metadata"
    )

    retriever = vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "score_threshold": 0.3
        }
    )

    return retriever

retriever = get_retriever()
retriever_tool = create_retriever_tool(
    retriever,
    "Retriever",
    "Retrieve relevant documents from the internal database."
)
#%%
#Define Tools
tools = [
    get_weather_from_city_name,
    get_weather_forecast_from_city_name,
    get_weather_forecast_from_city_name_date_phrase,
    retriever_tool
]
#%%
#Bind LLM to Tools
llm_with_tools = llm.bind_tools(tools)
#%%
#Define Nodes
def reasoner_node(state: MessagesState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

#%%
def check_for_tools(state: MessagesState) -> str:
    """
    Checks the last message in the state.
    If it has tool calls, returns "tools".
    Otherwise, returns "end".
    """
    last_message = state["messages"][-1]
    # Check if the AI message has any tool calls
    if last_message.tool_calls:
        return "tools"
    return "end"
#%%
#Build LangGraph
graph = StateGraph(MessagesState)
graph.add_node("reasoner", reasoner_node)
graph.add_node("tool", tool_node)
graph.add_edge(START, "reasoner")
graph.add_conditional_edges(
    "reasoner",
    check_for_tools,
    {
        "tools": "tool",
        "end": END
    }
)
graph.add_edge("tool", "reasoner")
app = graph.compile()
#%%
def get_langgraph_app():
    global app
    return app
#%%
def answer_query(user_query: str, chat_history: List = None) -> str:
    if chat_history is None:
        chat_history = []
    messages = chat_history + [HumanMessage(content=user_query)]

    langfuse_handler = CallbackHandler()

    config = {
        "recursion_limit": 50,
        "callbacks": [langfuse_handler]
    }
    
    app = get_langgraph_app()

    result_state = app.invoke({"messages": messages}, config=config)
    
    answer = result_state["messages"][-1].content
    return answer

# Run API with uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    print(answer_query("What is the weather in Berlin?"))
