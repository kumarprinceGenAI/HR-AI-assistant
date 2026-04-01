import os
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

QDRANT_PATH = "qdrant_data"
COLLECTION_NAME = "hr_documents"

def create_vector_store(documents):
    """
    Create Qdrant vector store and save locally to disk.
    If it exists, it will overwrite the collection.
    """
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )

    # Qdrant running in local mode (saving data to a local directory)
    vector_store = QdrantVectorStore.from_documents(
        documents,
        embedding,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME,
        force_recreate=True
    )
    
    return vector_store

def load_vector_store():
    """
    Load Qdrant index from the persistent local directory.
    """
    if not os.path.exists(QDRANT_PATH):
        raise FileNotFoundError(f"Qdrant dataset path '{QDRANT_PATH}' does not exist.")

    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )

    return QdrantVectorStore.from_existing_collection(
        embedding=embedding,
        path=QDRANT_PATH,
        collection_name=COLLECTION_NAME
    )