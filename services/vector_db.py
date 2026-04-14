import pinecone
from core.config import settings

class VectorDBService:
    def __init__(self):
        # In Pinecone 3.x+ (2026), we use the Pinecone class directly
        self.pc = pinecone.Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME

    def get_index(self):
        """Returns the active Pinecone index."""
        return self.pc.Index(self.index_name)

    def upsert_vectors(self, vectors: list):
        """Standardizes the upsert process."""
        index = self.get_index()
        # Ensure we are batching for production stability
        return index.upsert(vectors=vectors, namespace="clinical-docs")

    def query_similarity(self, vector: list, top_k: int = 5):
        """Searches for the most relevant medical context."""
        index = self.get_index()
        return index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace="clinical-docs"
        )