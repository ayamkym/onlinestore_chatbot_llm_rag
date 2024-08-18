import os
import pickle
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from groq import Groq
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Load the API key securely from environment variables
api_key = config('GROQ_API_KEY')

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Path to save the embeddings
EMBEDDINGS_FILE = os.path.join(os.path.dirname(__file__), "embeddings.pkl")

def load_data_from_db():
    from .models import Product
    text_data = []
    for product in Product.objects.all():
        image_url = product.image.url if product.image else "No image available"
        text_data.append(
            f"Name: {product.name}\n"
            f"Description: {product.description}\n"
            f"Price: ${product.price}\n"
            f"Stock: {product.stock}\n"
            f"Category: {product.category.name}\n"
            f"Image: {image_url}"
        )
    return text_data

def get_text_chunks(text_data):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for text in text_data:
        chunks.extend(text_splitter.split_text(text))
    return chunks

def create_and_save_vectorstore():
    text_data = load_data_from_db()
    text_chunks = get_text_chunks(text_data)

    embeddings = HuggingFaceEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(vectorstore, f)
    print(f"Embeddings created and saved to {EMBEDDINGS_FILE}")

def load_vectorstore():
    if not os.path.exists(EMBEDDINGS_FILE):
        raise FileNotFoundError(f"{EMBEDDINGS_FILE} not found. Ensure the file is present in the deployment environment.")

    with open(EMBEDDINGS_FILE, 'rb') as f:
        vectorstore = pickle.load(f)
    return vectorstore

def initialize_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever()
    llm = ChatGroq(api_key=api_key, model="llama-3.1-70b-versatile", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
    return qa_chain

def get_ai_response(query):
    try:
        vectorstore = load_vectorstore()
        qa_chain = initialize_qa_chain(vectorstore)
        result = qa_chain.invoke({"query": query})
        response = result.get("result", "No result found")
        source_documents = result.get("source_documents", [])
        
        return response, source_documents
    except Exception as e:
        print(f"Error processing query: {e}")
        return "An error occurred while processing your query.", []
