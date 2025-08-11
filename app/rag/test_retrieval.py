import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

time.sleep(2)

import chromadb
from sentence_transformers import SentenceTransformer

print("Script started (top of file)")

# Always resolve project root as two levels up from this file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
persist_dir = os.path.join(project_root, "app", "db", "chroma_db_test")
os.makedirs(persist_dir, exist_ok=True)
folder_path = os.path.join(project_root, "data", "textbooks")

print("ChromaDB absolute path:", persist_dir)
print("Textbooks folder absolute path:", folder_path)

chroma_client = chromadb.PersistentClient(path=persist_dir)
collection = chroma_client.get_or_create_collection("textbook_chunks")
print("Using ChromaDB directory:", persist_dir)

# Initialize SentenceTransformer model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def setup_openai_client():
    """Set up OpenAI client using environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found in .env file")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        return None
    
    print("✅ OpenAI API key loaded successfully")
    return OpenAI(api_key=api_key)

def get_embedding(text):
    return embedder.encode(text).tolist()

def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas']
    )
    # Defensive: Check if results are present
    if not results or not results.get('documents') or not results['documents'] or not results['documents'][0]:
        return []
    if not results.get('metadatas') or not results['metadatas'] or not results['metadatas'][0]:
        return []
    # Returns a list of (chunk_text, metadata) tuples
    return list(zip(results['documents'][0], results['metadatas'][0]))

def answer_with_openai(question, retrieved_chunks, model='gpt-3.5-turbo'):
    """Answer questions using OpenAI."""
    client = setup_openai_client()
    if client is None:
        return "Error: OpenAI API key not configured. Please check your .env file."
    
    # Build context from retrieved chunks
    context = "\n\n".join([f"From {meta['filename']} (page {meta['page']}):\n{chunk}" for chunk, meta in retrieved_chunks])
    
    # Create the prompt
    system_prompt = """You are a helpful CPA study assistant. Use the provided textbook excerpts to answer questions accurately and comprehensively. 
    If the context doesn't contain enough information to answer the question, say so clearly.
    Always cite the source (filename and page) when possible."""
    
    user_prompt = f"""Use the following textbook excerpts to answer the question.

Context:
{context}

Question: {question}

Please provide a clear, accurate answer based on the context provided."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused answers
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

print("Collection count:", collection.count())

if __name__ == "__main__":
    print("Inside main block")
    question = input("Enter a question to test retrieval: ")
    top_chunks = retrieve_relevant_chunks(question)
    print(f"Retrieved {len(top_chunks)} chunks.")
    if not top_chunks:
        print("No relevant chunks found. Try a different question or check your ChromaDB data.")
    else:
        for i, (chunk, meta) in enumerate(top_chunks, 1):
            print(f"\nResult {i}:")
            print(f"From {meta['filename']} (page {meta['page']}):")
            print(chunk)
            print("-" * 40)
        
        # Ask if user wants an AI-generated answer
        answer_question = input("\nWould you like an AI-generated answer? (y/n): ")
        if answer_question.lower() in ['y', 'yes']:
            print("\nGenerating answer with OpenAI...")
            answer = answer_with_openai(question, top_chunks, model='gpt-3.5-turbo')
            print("\nOpenAI Answer:\n", answer)