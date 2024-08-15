
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq  # Ensure this import is correct
from langchain_community.vectorstores import FAISS
from groq import Groq
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Load the API key securely from environment variables
api_key = config('GROQ_API_KEY')

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

def load_data_from_db():
    from .models import Product  # Ensure your models are correctly imported
    text_data = []
    for product in Product.objects.all():
        # Append product details to text_data
        text_data.append(
            f"Name: {product.name}\nDescription: {product.description}\nPrice: ${product.price}\nStock: {product.stock}\nCategory: {product.category.name}"
        )
    return text_data

def get_text_chunks(text_data):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for text in text_data:
        chunks.extend(text_splitter.split_text(text))
    return chunks

def get_vectorstore(text_chunks):
    # Ensure HuggingFaceEmbeddings is correctly set up
    embeddings = HuggingFaceEmbeddings()
    # Build FAISS vectorstore from text chunks and embeddings
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Initialize the QA chain
def initialize_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever()
    # Configure the LLM with correct parameters
    llm = ChatGroq(api_key=api_key, model="llama-3.1-70b-versatile", temperature=0)
    # Build the RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    return qa_chain

## Main function to handle chatbot responses
def get_ai_response(query):
    try:
        # Load data and initialize vectorstore
        text_data = load_data_from_db()
        text_chunks = get_text_chunks(text_data)
        vectorstore = get_vectorstore(text_chunks)
        
        # Initialize QA chain
        qa_chain = initialize_qa_chain(vectorstore)
        
        # Get response from QA chain
        result = qa_chain.invoke({"query": query})
        response = result.get("result", "No result found")
        source_documents = result.get("source_documents", [])
        
        return response, source_documents
    except Exception as e:
        print(f"Error processing query: {e}")
        return "An error occurred while processing your query.", []

