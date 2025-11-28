import yaml
from dataclasses import dataclass

@dataclass
class QdrantConfig:
    """Configuration for Qdrant settings"""
    host: str
    port: int
    collection_name: str
    vector_size: int
    distance: str

@dataclass
class EmbeddingModelConfig:
    """Configuration for embedding model settings"""    
    name: str
    dimension: int
    chunk_size: int  # number of characters per text chunk
    chunk_overlap: int  # number of overlapping characters between chunks

@dataclass
class DirectoryConfig:
    """Configuration for source and processed data directories"""
    source_data_dir: str
    processed_data_dir: str


def load_config_from_yaml(path: str) -> tuple[QdrantConfig, EmbeddingModelConfig, DirectoryConfig]:
    """Load and validate configuration from YAML file"""
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    
    # Validate required keys exist
    if "qdrant" not in raw or "source_data" not in raw or "processed_data" not in raw or "embedding_model" not in raw:
        raise ValueError("Configuration must contain 'qdrant', 'source_data', 'processed_data', and 'embedding_model' sections")
    
    # Create nested dataclass instances
    qdrant_config = QdrantConfig(**raw["qdrant"])
    embed_config = EmbeddingModelConfig(**raw["embedding_model"])
    directory_config = DirectoryConfig(
        source_data_dir=raw["source_data"]["directory"],
        processed_data_dir=raw["processed_data"]["directory"]
    )
    

    return (qdrant_config, embed_config, directory_config)