import os
import sys
import django
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document  # Import Document
from decouple import config
from dotenv import load_dotenv

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Load environment variables from .env file
load_dotenv()

# Define the embedding model
embedding_model_id = "BAAI/bge-small-en-v1.5"
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_id)

def load_data_from_db():
    from shop.models import Product  # Adjust 'shop' to your actual app name
    text_data = []
    try:
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
    except Exception as e:
        print(f"Error loading data from the database: {e}")
    return text_data

def get_text_chunks(text_data):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    try:
        for text in text_data:
            chunks.extend(text_splitter.split_text(text))
    except Exception as e:
        print(f"Error splitting text into chunks: {e}")
    return chunks

# Load data from the database
text_data = load_data_from_db()

# Split the data into chunks
all_chunks = get_text_chunks(text_data)

# Wrap chunks in Document objects
documents = [Document(page_content=chunk) for chunk in all_chunks]

# Embed chunks and save the embeddings into a FAISS index
try:
    embeddings_db = FAISS.from_documents(documents, embeddings)
    # Ensure the directory exists
    os.makedirs("./db", exist_ok=True)
    # Save the FAISS index locally
    embeddings_db.save_local("./db/faiss_index")
    print("FAISS index saved successfully.")
except Exception as e:
    print(f"Error creating or saving FAISS index: {e}")
