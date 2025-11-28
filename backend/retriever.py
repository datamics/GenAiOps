from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
try:
    from config import QDRANT_URL, QDRANT_PORT, QDRANT_COLLECTION
except ModuleNotFoundError:
    from backend.config import QDRANT_URL, QDRANT_PORT, QDRANT_COLLECTION

class QdrantRetrievalService:
    def __init__(self, qdrant_url: str, collection_name: str, embedding, top_k: int = 5):
        """
        Initializes the QdrantRetrievalService with necessary configurations.

        Args:
            qdrant_url (str): URL of the Qdrant instance.
            collection_name (str): Name of the Qdrant collection to query.
            embedding: The embedding model to use.
            top_k (int): Number of top results to retrieve. Defaults to 5.
        """
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            port=6333,
            https=False
        )
        self.vectorstore = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=collection_name,
            embedding=embedding
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})

    def query(self, input_text: str):
        """
        Queries the retriever with the provided input text.

        Args:
            input_text (str): The input query to retrieve related data.

        Returns:
            list: A list of results from the retriever.
        """
        return self.retriever.invoke(input=input_text)

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT)

    vector_db = QdrantRetrievalService(
        qdrant_url=QDRANT_URL,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings
    )

    retriever = vector_db

    return retriever
