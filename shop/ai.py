import os
import pickle
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from groq import Groq
from decouple import config
from dotenv import load_dotenv
from threading import Lock

load_dotenv()

# Load the API key securely from environment variables
api_key = config('GROQ_API_KEY')

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Path to save the embeddings
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "embeddings.pkl")

# Cache for the vector store
vectorstore_cache = None
cache_lock = Lock()

def load_vectorstore():
    """
    Load the vector store from the pre-saved embeddings file.
    """
    if not os.path.exists(EMBEDDINGS_FILE):
        raise FileNotFoundError(f"{EMBEDDINGS_FILE} not found. Ensure the file is present in the deployment environment.")
    
    with open(EMBEDDINGS_FILE, 'rb') as f:
        vectorstore = pickle.load(f)
    return vectorstore

def get_vectorstore():
    """
    Get the vector store from cache or load it if not cached.
    """
    global vectorstore_cache
    with cache_lock:
        if vectorstore_cache is None:
            vectorstore_cache = load_vectorstore()
    return vectorstore_cache

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
