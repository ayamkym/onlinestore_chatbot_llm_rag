import os
import json
import time
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from groq import Groq
from decouple import config
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage

# Load environment variables
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
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )
    return qa_chain

# Define prompts
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

# Initialize contextualize_q_chain
llm = ChatGroq(api_key=api_key, model="llama-3.1-70b-versatile", temperature=0)
contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

qa_system_prompt = """You are an assistant for providing customer support for an online clothing store. \
Use the following pieces of retrieved context to answer the customer’s query. \
If you don't know the answer, just say that you don't know. \
Provide a concise response, using up to three sentences if necessary.\

{context}"""
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

def contextualized_question(input: dict):
    """
    Determine the appropriate question to use based on chat history.
    """
    if input.get("chat_history"):
        return contextualize_q_chain
    else:
        return input.get("question")

def get_ai_response(query, session_id, request):
    """
    Get AI response for the given query using the initialized QA chain with chat history.
    """
    try:
        vectorstore = get_vectorstore()
        if not vectorstore:
            return "Failed to load vector store."

        qa_chain = initialize_qa_chain(vectorstore)

        # Retrieve chat history from Django session
        from django.contrib.sessions.models import Session
        try:
            session = Session.objects.get(session_key=session_id)
            session_data = json.loads(session.get_decoded().get('chat_history', '[]'))
        except Session.DoesNotExist:
            session_data = []
        
        chat_history = ChatMessageHistory()
        for msg in session_data:
            if msg['type'] == 'human':
                chat_history.add_message(HumanMessage(content=msg['content']))
            else:
                chat_history.add_message(AIMessage(content=msg['content']))

        def extract_messages(chat_history: ChatMessageHistory) -> list:
            return [
                HumanMessage(content=msg.content) if isinstance(msg, HumanMessage)
                else AIMessage(content=msg.content)
                for msg in chat_history.messages
            ]

        # Initialize chains
        rag_chain = (
            RunnablePassthrough.assign(
                context=contextualized_question | vectorstore.as_retriever()
            )
            | qa_prompt
            | ChatGroq(api_key=api_key, model="llama-3.1-70b-versatile", temperature=0)
        )

        # Retry logic for temporary issues
        for attempt in range(3):
            try:
                result = rag_chain.invoke(
                    {
                        "question": query,
                        "chat_history": extract_messages(chat_history)
                    }
                )

                # Debugging line to inspect the result
                #print("Raw result:", result)  # Inspect the raw result from the model

                # Ensure result is not None and has a content attribute
                if result and hasattr(result, 'content'):
                    response = result.content
                else:
                    response = "Unexpected result format"

                # Update chat history
                chat_history.add_message(HumanMessage(content=query))
                chat_history.add_message(AIMessage(content=response))

                # Save updated chat history back to Django session
                session_data = [{'type': 'human', 'content': msg.content} if isinstance(msg, HumanMessage)
                                else {'type': 'ai', 'content': msg.content}
                                for msg in chat_history.messages]
                request.session['chat_history'] = json.dumps(session_data)
                request.session.save()

                return response
            except Exception as e:
                print(f"Error processing query (attempt {attempt + 1}): {e}")
                if attempt < 2:  # Retry if not the last attempt
                    time.sleep(2)
                else:
                    return "An error occurred while processing your query."
    except Exception as e:
        print(f"Error processing query: {e}")
        return "An error occurred while processing your query."
