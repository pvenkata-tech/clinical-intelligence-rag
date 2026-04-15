# Streamlit UI Guide 💻

Interactive clinical intelligence dashboard for document management and analysis.

## Starting the UI

```bash
streamlit run ui/app.py
```

The dashboard will be available at:
- **Local:** http://localhost:8501
- **Network:** http://<your-ip>:8501

## Features

### 📁 Document Upload
Upload clinical PDF documents directly from the sidebar:
1. Click "Upload Clinical PDF" in the left panel
2. Select a markdown `.pdf` file from your system
3. Click "Process & Index Document"
4. The system will automatically:
   - Parse the PDF using PyPDF2
   - Split into 1000-character chunks with medical context awareness
   - Apply PHI scrubbing (if enabled)
   - Generate embeddings
   - Index in Pinecone vector database

**Supported Formats:** PDF files only

**Max File Size:** Limited by Streamlit default (200MB)

**Processing Time:** Typically 10-30 seconds for standard clinical documents

### 💬 Chat Interface
Ask natural language questions about the uploaded documents:

1. Type your question in the chat input (e.g., "What is the patient's oxygen saturation?")
2. The RAG system will:
   - Search documents for relevant context
   - Compress and re-rank results
   - Generate an AI response grounded in the documents
3. View the response with source attribution

**Example Questions:**
- "What is the patient's current diagnosis?"
- "What medications is the patient taking?"
- "What is the medical plan for treatment?"
- "Are there any allergies or contraindications?"

### 📥 Download Analysis
Save clinical analysis to your local machine:

1. After receiving an AI response, look for the **"📥 Download Clinical Analysis"** button
2. Click to download as `clinical_summary.txt`
3. File contains the complete AI analysis for medical records

**File Format:** Plain text (.txt)

**Use Cases:**
- Medical record documentation
- Compliance archiving
- Sharing with other providers
- Offline review

### 📚 Evidence View
Expand the **"View Evidence"** section to see source documents:

Displays all clinical document chunks that informed the AI's response:
- **Source Segment [N]:** The actual text from your document
- Ranked by relevance to the question
- Helps verify answer accuracy and grounding

## User Workflow

### Step 1: Upload Documents
```
1. Open Streamlit app
2. Click sidebar "Upload Clinical PDF"
3. Select patient_records.pdf
4. Click "Process & Index Document"
5. Wait for ✅ "Successfully indexed X segments!"
```

### Step 2: Explore Clinical Data
```
1. Type question in chat input
2. Receive AI-powered response
3. Review evidence in expandable section
```

### Step 3: Export Findings
```
1. Click "📥 Download Clinical Analysis"
2. Save clinical_summary.txt locally
3. Use in medical record systems
```

## Configuration

### Enable/Disable Features

Edit `ui/app.py` to customize:

```python
# Enable PHI scrubbing
ingestor = ClinicalIngestor(enable_phi_scrubbing=True)

# Adjust retrieval depth
vdb.similarity_search(prompt, k=5)  # More context

# Disable contextual compression for testing
docs = vdb.similarity_search(prompt, enable_compression=False)
```

### Customize Appearance

```python
# In ui/app.py
st.set_page_config(
    page_title="Clinical Intel RAG",
    page_icon="🏥",
    layout="wide"  # or "centered"
)
```

## Settings

### Active Provider Display
Shows which LLM provider is currently active (from `.env`):
- **OpenAI (GPT-4o)** - Fastest responses
- **Anthropic (Claude 3.5)** - Best reasoning
- **AWS Bedrock** - HIPAA compliant

Switch providers by editing `.env`:
```bash
LLM_PROVIDER=OPENAI  # Change and reload app
```

## Best Practices

✅ **DO:**
- Upload one patient's documents at a time
- Ask specific, clinical questions
- Review evidence to verify ground truth
- Use for clinical decision support (not primary diagnosis)

❌ **DON'T:**
- Upload unencrypted PHI without scrubbing enabled
- Rely solely on AI for critical decisions
- Use for sensitive cardiac or ICU patients without review
- Override doctor's clinical judgment

## Performance Tips

### Faster Responses
```python
# Reduce context chunks
similarity_search(query, k=3)  # Default is 4

# Disable compression
enable_compression=False
```

### Better Context
```python
# Increase context chunks
similarity_search(query, k=10)  # More thorough

# Enable detailed evidence view
st.expander("📚 View Evidence", expanded=True)
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
```bash
pip install streamlit>=1.28.0
```

**"ConnectionError: Failed to connect to Pinecone"**
- Check `.env` PINECONE_API_KEY is correct
- Verify PINECONE_INDEX_NAME exists in your account
- Ensure API key has proper permissions

**"No documents indexed in database"**
```bash
# Re-upload documents
cd data/samples/
# Drag PDFs here, then process via UI
```

**Slow upload processing**
- Large PDFs (>50MB) may take 60+ seconds
- Check network connection to Pinecone
- Monitor CPU/memory in Activity Monitor

## Deployment

Deploy with Docker:
```bash
docker-compose up --build
```

The UI service runs on port 8501 with automatic restarts.

See [DOCKER.md](DOCKER.md) for production deployment details.

## Next Steps

- **API Integration:** See [API.md](API.md)
- **Advanced Features:** See [FEATURES.md](FEATURES.md)
- **Setup Guide:** See [SETUP.md](SETUP.md)
