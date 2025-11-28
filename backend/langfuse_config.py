import os
from langfuse import Langfuse, get_client, observe
from dotenv import load_dotenv

_langfuse_client = None
load_dotenv()

def setup_telemetry() -> Langfuse:
    """
    Initalize Langfuse.

    Expects the following environment variables to be set:
        LANGFUSE_PUBLIC_KEY
        LANGFUSE_SECRET_KEY
        LANGFUSE_HOST
    """
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client

    _langfuse_client = Langfuse(
        public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
        host=os.environ.get("LANGFUSE_HOST"),
    )

    return _langfuse_client
