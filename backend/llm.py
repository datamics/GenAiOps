from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from config import GOOGLE_API_KEY
except ModuleNotFoundError:
    from backend.config import GOOGLE_API_KEY

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        streaming=True,
        google_api_key=GOOGLE_API_KEY,
        convert_system_message_to_human=True
    )
