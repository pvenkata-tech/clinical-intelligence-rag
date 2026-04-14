from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ClinicalIngestor:
    def __init__(self):
        # Healthcare-specific splitting: keep paragraphs together for context
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )

    def process_document(self, file_path: str):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        return self.splitter.split_documents(documents)