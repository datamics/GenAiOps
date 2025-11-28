"""
PDF to Qdrant Ingestion Pipeline.

This module handles the extraction of text from PDF files, chunking,
embedding generation, and uploading to Qdrant vector database.
"""

import logging
import os
from typing import List
from utils.load_config import load_config_from_yaml
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models

# Configure logging
DEBUG_MODE = True

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if DEBUG_MODE else '%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress verbose logging from third-party libraries unless in debug mode
if not DEBUG_MODE:
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    
# ----------------------------------------------------------------------------------------------   
    
class DocumentProcessor:
    
    def __init__(self, qdrant_config, embed_config, **kwargs):

        # Qdrant configuration
        self.QDRANT_HOST = qdrant_config.host   
        self.QDRANT_PORT = qdrant_config.port
        self.QDRANT_COLLECTION_NAME = qdrant_config.collection_name
        self.DISTANCE_METRIC = qdrant_config.distance

        # Embedding model configuration
        self.EMBEDDING_MODEL_NAME = embed_config.name
        self.EMBEDDING_DIMENSION = qdrant_config.vector_size
    
        # Text chunking configuration
        self.CHUNK_SIZE = embed_config.chunk_size
        self.CHUNK_OVERLAP = embed_config.chunk_overlap
        
    def extract_chunks_from_pdf(self, pdf_path: str) -> List:
        """
            Extract and chunk text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of document chunks

        Raises:
            Exception: If PDF loading or splitting fails
        """
        
        logger.debug("Extracting text from %s", pdf_path)
        try:
            loader = PyPDFLoader(file_path=pdf_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.debug("Successfully extracted %d chunks from PDF", len(chunks))
            return chunks   
        except Exception as e:
            logger.error("Error reading PDF: %s", e)
            return None
            


    def get_embedding_model(self) -> HuggingFaceEmbeddings:
        """
        Load the HuggingFace embedding model.

        Returns:
            Initialized HuggingFaceEmbeddings model
        """
        logger.debug("Loading embedding model '%s'", self.EMBEDDING_MODEL_NAME)
        model = HuggingFaceEmbeddings(model_name=self.EMBEDDING_MODEL_NAME)
        logger.debug("Model loaded successfully")
        return model


    def get_qdrant_client(self) -> QdrantClient:
        """
        Initialize and return the Qdrant client.

        Returns:
            Initialized QdrantClient instance
        """
        logger.debug("Connecting to Qdrant at %s:%s", self.QDRANT_HOST, self.QDRANT_PORT)
        client = QdrantClient(host=self.QDRANT_HOST, port=self.QDRANT_PORT)
        return client


    def setup_qdrant_collection(self, client: QdrantClient) -> None:
        """
        Create a Qdrant collection if it does not already exist.

        Args:
            client: Initialized QdrantClient instance
        """
        if client.collection_exists(collection_name=self.QDRANT_COLLECTION_NAME):
            logger.debug("Collection '%s' already exists", self.QDRANT_COLLECTION_NAME)
        else:
            logger.info("Creating collection '%s'", self.QDRANT_COLLECTION_NAME)
            client.create_collection(
                collection_name=self.QDRANT_COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=self.EMBEDDING_DIMENSION,
                    distance=self.DISTANCE_METRIC,
                    on_disk=True
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0,
                    default_segment_number=4
                ),
                quantization_config=models.BinaryQuantization(
                    binary=models.BinaryQuantizationConfig(always_ram=True),
                )
            )
            logger.info("Collection created successfully")


    def vectorize_and_upload(
        self,
        model: HuggingFaceEmbeddings,
        documents: List
    ) -> None:
        """
        Vectorize text chunks and upload them to Qdrant.

        Args:
            model: Initialized embedding model
            documents: List of document chunks to vectorize

        Raises:
            Exception: If upload to Qdrant fails
        """
        try:
            logger.debug("Vectorizing and uploading %d documents", len(documents))
            QdrantVectorStore.from_documents(
                documents=documents,
                embedding=model,
                collection_name=self.QDRANT_COLLECTION_NAME,
                url=self.QDRANT_HOST,
                port=self.QDRANT_PORT,
                https=False,
                prefer_grpc=False,
            )
            logger.debug("Successfully uploaded all vectors to Qdrant")
        except Exception as e:
            logger.error("Error uploading points to Qdrant: %s", e)
            raise


    def process_pdf_file(self, pdf_file_path: str) -> None:
        """
        Process a single PDF file and upload to Qdrant.

        Args:
            pdf_file_path: Path to the PDF file

        Raises:
            FileNotFoundError: If the PDF file does not exist
            ValueError: If no chunks are extracted from the PDF
        """
        if not os.path.exists(pdf_file_path):
            logger.error("File not found at %s", pdf_file_path)
            raise FileNotFoundError(f"File not found: {pdf_file_path}")

        pdf_name = os.path.basename(pdf_file_path)
        logger.info("Processing: %s", pdf_name)

        try:
            qdrant_client = self.get_qdrant_client()
            embedding_model = self.get_embedding_model()
            self.setup_qdrant_collection(qdrant_client)
            
            documents = self.extract_chunks_from_pdf(pdf_file_path)
            if not documents:
                logger.error("No chunks extracted from PDF")
                raise ValueError("No chunks extracted from PDF")
            
            self.vectorize_and_upload(embedding_model, documents)
            
            logger.info("Successfully processed: %s", pdf_name)
            
        except Exception as e:
            logger.error("An error occurred during processing: %s", e)
            raise


    def main(self, pdf_file_path: str = None, **kwargs) -> None:
        """
        Main function to process a PDF file and upload to Qdrant.

        Args:
            pdf_file_path: Path to the PDF file to process

        Raises:
            ValueError: If no PDF file path is provided
        """
        
        if not pdf_file_path:
            raise ValueError("Please provide a valid PDF file path.")
        self.process_pdf_file(pdf_file_path)


if __name__ == "__main__":
    
    config_file_path = os.path.join("dags", "config", "ingestion_dev.yaml")
    qdrant_config, embed_config, directory_config = load_config_from_yaml(config_file_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dp = DocumentProcessor(qdrant_config, embed_config)
    dp.main(pdf_file_path=os.path.join(base_dir, "../../source_data", "Paris.pdf")) 
