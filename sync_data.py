from core.ingestion import ClinicalIngestor
from services.vector_db import VectorStoreManager
import os

def sync():
    print("📂 Loading PDFs from data/samples...")
    ingestor = ClinicalIngestor()
    vector_manager = VectorStoreManager()
    
    # Process every PDF in your data/samples folder
    for file in os.listdir("data/samples"):
        if file.endswith(".pdf"):
            path = f"data/samples/{file}"
            print(f"📄 Processing {file}...")
            chunks = ingestor.process_document(path)
            vector_manager.add_documents(chunks)
            
    print("✅ All clinical data indexed in Pinecone!")

if __name__ == "__main__":
    sync()