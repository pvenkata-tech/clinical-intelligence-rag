from core.orchestrator import ClinicalRAGOrchestrator
from services.vector_db import VectorStoreManager

def run_test_query():
    # 1. Initialize
    print("🧠 Initializing Clinical RAG Orchestrator...")
    orchestrator = ClinicalRAGOrchestrator()
    vector_manager = VectorStoreManager()

    # 2. The Question
    question = "What is the patient's oxygen saturation and what is the doctor's plan for oxygen?"
    print(f"❓ Question: {question}")

    # 3. Retrieval Step
    print("🔍 Searching Pinecone for relevant clinical context...")
    # We search for the top 3 most relevant segments from your PDF
    docs = vector_manager.similarity_search(question, k=3)
    context = "\n---\n".join([d.page_content for d in docs])

    # 4. Generation Step
    print("🤖 Generating answer using the selected LLM Provider...")
    answer = orchestrator.query(question, context)

    print("\n" + "="*50)
    print("📝 CLINICAL RESPONSE:")
    print(answer)
    print("="*50 + "\n")

if __name__ == "__main__":
    run_test_query()