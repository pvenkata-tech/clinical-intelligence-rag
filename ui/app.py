import streamlit as st
import os
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import ClinicalRAGOrchestrator
from services.vector_db import VectorStoreManager
from core.ingestion import ClinicalIngestor

# 1. Page Configuration
st.set_page_config(page_title="Clinical Intel RAG", page_icon="🏥", layout="wide")

# 2. Sidebar: Settings & Upload
with st.sidebar:
    st.title("🛡️ Clinical Admin")
    st.info(f"Active Provider: **{os.getenv('LLM_PROVIDER', 'OPENAI')}**")
    
    st.divider()
    st.subheader("📁 Ingest New Records")
    uploaded_file = st.file_uploader("Upload Clinical PDF", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process & Index Document"):
            with st.spinner("Analyzing and vectorizing..."):
                # Save temp file
                temp_path = f"data/samples/{uploaded_file.name}"
                os.makedirs("data/samples", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Run Ingestion
                ingestor = ClinicalIngestor()
                chunks = ingestor.process_document(temp_path)
                
                vdb = VectorStoreManager()
                vdb.add_documents(chunks)
                
                st.success(f"Successfully indexed {len(chunks)} segments!")

# 3. Main Chat Interface
st.title("🏥 Clinical Intelligence Dashboard")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Query Logic
if prompt := st.chat_input("Ask about patient history..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving medical context..."):
            vdb = VectorStoreManager()
            orch = ClinicalRAGOrchestrator()
            
            # Retrieval
            docs = vdb.similarity_search(prompt, k=3)
            context = "\n---\n".join([d.page_content for d in docs])
            
            # Generation
            response = orch.query(prompt, context)
            
            st.markdown(response)
            
            # Download button for analysis
            st.download_button(
                label="📥 Download Clinical Analysis",
                data=response,
                file_name="clinical_summary.txt",
                mime="text/plain"
            )
            
            # Show Sources
            with st.expander("📚 View Evidence"):
                for i, doc in enumerate(docs):
                    st.caption(f"Source Segment {i+1}:")
                    st.write(doc.page_content)

    st.session_state.messages.append({"role": "assistant", "content": response})