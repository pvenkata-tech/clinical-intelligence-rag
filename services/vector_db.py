from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from services.embeddings import EmbeddingService
from core.config import settings

class VectorStoreManager:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embeddings = EmbeddingService.get_embeddings()

    def get_vector_store(self):
        return PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )

    def add_documents(self, documents):
        """Adds processed LangChain documents to Pinecone"""
        vector_store = self.get_vector_store()
        return vector_store.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4):
        """Retrieves the most relevant clinical context"""
        vector_store = self.get_vector_store()
        return vector_store.similarity_search(query, k=k)