import os
import pickle
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from groq import Groq
from decouple import config
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Load the API key securely from environment variables
api_key = config('GROQ_API_KEY')

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Define the embedding model
embedding_model_id = "BAAI/bge-small-en-v1.5"
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_id)

def get_vectorstore():
    """
    Load the FAISS vector store from the local file system.
    """
    try:
        return FAISS.load_local("./db/faiss_index", embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None


def initialize_qa_chain(vectorstore):
    """
    Initialize the QA chain using the loaded vector store.
    """
    retriever = vectorstore.as_retriever()
    llm = ChatGroq(api_key=api_key, model="llama-3.1-70b-versatile", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    return qa_chain

def get_ai_response(query):
    """
    Get AI response for the given query using the initialized QA chain.
    """
    try:
        vectorstore = get_vectorstore()
        qa_chain = initialize_qa_chain(vectorstore)
        result = qa_chain.invoke({"query": query})
        response = result.get("result", "No result found")
        source_documents = result.get("source_documents", [])
        
        return response, source_documents
    except Exception as e:
        print(f"Error processing query: {e}")
        return "An error occurred while processing your query.", []
