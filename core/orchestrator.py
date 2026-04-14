from models.factory import ModelFactory
from core.ingestion import ClinicalIngestor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class ClinicalRAGOrchestrator:
    def __init__(self):
        # Initialize the model using our flexible factory
        self.model = ModelFactory.get_model()
        self.ingestor = ClinicalIngestor()
        self.parser = StrOutputParser()

    def get_rag_chain(self, context: str):
        """
        Creates a chain that uses retrieved medical context to answer questions.
        This is the core RAG logic.
        """
        template = """
        You are a Senior Medical AI Assistant. Use the following pieces of retrieved 
        context to answer the user's question. If the answer is not in the context, 
        say that you don't know based on the provided data.
        
        Context: {context}
        
        Question: {question}
        
        Answer (Be professional and cite context if possible):
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # The LCEL (LangChain Expression Language) Chain
        return prompt | self.model | self.parser

    def query(self, question: str, context: str):
        chain = self.get_rag_chain(context)
        return chain.invoke({"question": question, "context": context})