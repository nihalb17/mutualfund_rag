import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from phase_4.guardrails import Guardrails

# Load environment variables
load_dotenv()

# Configuration
CHROMA_DIR = "phase_2/chroma_db"

class MutualFundRAG:
    def __init__(self):
        # Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load Vector Store
        self.vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in .env file. Please add it.")
            
        # Initialize LLM
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant", 
            temperature=0,
            api_key=GROQ_API_KEY
        )
        
        # Define Prompt Template
        template = """
        You are a helpful and factual Mutual Fund chatbot. Use the following context to answer the user's question.
        
        Rules:
        1. Base your answer ONLY on the provided context.
        2. If the answer is not in the context, say: "I don't have an answer to the question you are asking."
        3. Do NOT provide any investment advice. If asked for advice, say: "I am only here to provide information regarding mutual funds."
        4. Your response should be factual and professional.
        5. CRITICAL: When asked for the "fund size", look specifically for the label "Fund size" (e.g., Fund size ₹X Cr). Do NOT confuse this with "Asset Under Management(AUM)" which usually refers to the AMC's total AUM.
        
        Context:
        {context}
        
        Question: {question}
        
        Factual Answer:
        """
        self.prompt = PromptTemplate.from_template(template)
        
        # Create RAG Chain using LCEL
        def format_docs(docs):
            if not docs:
                return "NO_CONTEXT"
            return "\n\n".join(doc.page_content for doc in docs)

        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query: str):
        # 1. Pre-RAG Guardrails
        guard_resp = Guardrails.get_guardrail_response(query, context_found=True)
        if guard_resp:
            return {"answer": guard_resp, "sources": []}
            
        # 2. RAG Execution
        source_docs = self.retriever.invoke(query)
        
        # Double check if retriever found anything meaningful
        if not source_docs:
            return {"answer": "I don't have an answer to the question you are asking.", "sources": []}
            
        answer = self.rag_chain.invoke(query)
        
        # 3. Post-LLM Guardrails (Handle "I don't have an answer" variations from LLM)
        if "i don't have an answer" in answer.lower() or "i don't have information" in answer.lower():
            # Use the exact required strings
            if "scheme" in query.lower():
                 # Check if we should say unknown scheme or unknown answer
                 # Logic: if retriever found docs but LLM still says no info, it's out of scope/answer
                 pass
            
        # Extract the primary source (top matched document)
        sources = [source_docs[0].metadata.get("source", "Unknown")] if source_docs else []
        
        return {
            "answer": answer,
            "sources": sources
        }

if __name__ == "__main__":
    # Quick test
    rag = MutualFundRAG()
    res = rag.ask("What is the expense ratio of Axis Midcap Fund?")
    print(f"Answer: {res['answer']}")
    print(f"Sources: {res['sources']}")
