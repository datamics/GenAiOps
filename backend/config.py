import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

# API Keys and Config
GOOGLE_API_KEY = os.environ.get("LLM_API_KEY")
QDRANT_URL = os.environ.get("qdrant")
QDRANT_PORT = int(os.environ.get("qdrant_port", "6333"))
QDRANT_COLLECTION = os.environ.get("qdrant_collection")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST")


'''langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST
)

prompt_obj = langfuse.get_prompt("default", label="production")
SYSTEM_PROMPT = prompt_obj

if __name__ == "__main__":
    print(f"Loaded Prompt Version: {prompt_obj.version}")
    print(SYSTEM_PROMPT)
'''

# Prompts
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
