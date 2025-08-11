from flask import Flask, render_template, request, jsonify, session
import os
import random
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Set up project paths
project_root = os.path.abspath(os.path.dirname(__file__))
questions_folder = os.path.join(project_root, "data", "questions")
textbooks_folder = os.path.join(project_root, "data", "textbooks")
chroma_db_path = os.path.join(project_root, "db", "chroma_db_test")

def setup_openai_client():
    """Set up OpenAI client using environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        return None
    
    return OpenAI(api_key=api_key)

def load_questions_from_folder(folder_path):
    """Load practice questions from PDF files."""
    questions = []
    if not os.path.exists(folder_path):
        return questions
        
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            full_text += "\n" + page_text
                    
                    # Use regex to extract questions
                    pattern = r'(Question [A-Z]-\d+ \([^)]+\)[\s\S]*?)(?=Question [A-Z]-\d+ \(|\Z)'
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for q in matches:
                        # Remove everything after 'SUGGESTED ANSWER:' if present
                        marker = 'SUGGESTED ANSWER:'
                        idx = q.upper().find(marker)
                        if idx != -1:
                            q = q[:idx].strip()
                        if len(q.strip()) > 20:
                            questions.append({'text': q.strip(), 'source': filename})
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return questions

def setup_embedding_model():
    """Set up sentence transformer model for embeddings."""
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model
    except Exception as e:
        print(f"Error setting up embedding model: {e}")
        return None

def setup_chroma_client():
    """Set up ChromaDB client."""
    try:
        client = chromadb.PersistentClient(path=chroma_db_path)
        return client
    except Exception as e:
        print(f"Error setting up ChromaDB: {e}")
        return None

def retrieve_relevant_chunks(query, n_results=3):
    """Retrieve relevant chunks from ChromaDB."""
    client = setup_chroma_client()
    embedding_model = setup_embedding_model()
    
    if not client or not embedding_model:
        return []
    
    try:
        # Get the collection (create if it doesn't exist)
        collection = client.get_or_create_collection("textbook_chunks")
        
        # Generate embedding for the query
        query_embedding = embedding_model.encode([query]).tolist()
        
        # Search for relevant chunks using embeddings
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        chunks = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                chunks.append((doc, metadata))
        
        return chunks
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return []

def ingest_documents_to_chromadb():
    """Ingest textbook documents into ChromaDB."""
    client = setup_chroma_client()
    embedding_model = setup_embedding_model()
    
    if not client or not embedding_model:
        print("Failed to setup ChromaDB or embedding model")
        return False
    
    if not os.path.exists(textbooks_folder):
        print(f"Textbooks folder not found: {textbooks_folder}")
        return False
    
    try:
        collection = client.get_or_create_collection("textbook_chunks")
        
        # Check if collection already has data
        if collection.count() > 0:
            print(f"Collection already has {collection.count()} documents")
            return True
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        chunk_id = 0
        
        for filename in os.listdir(textbooks_folder):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(textbooks_folder, filename)
                try:
                    with pdfplumber.open(pdf_path) as pdf:
                        for page_num, page in enumerate(pdf.pages):
                            page_text = page.extract_text()
                            if page_text and len(page_text.strip()) > 50:
                                # Split into chunks (roughly 500 characters each)
                                chunks = [page_text[i:i+500] for i in range(0, len(page_text), 500)]
                                
                                for chunk in chunks:
                                    if len(chunk.strip()) > 50:
                                        documents.append(chunk.strip())
                                        metadatas.append({
                                            'filename': filename,
                                            'page': page_num + 1
                                        })
                                        ids.append(f"chunk_{chunk_id}")
                                        chunk_id += 1
                                        
                                        # Generate embeddings in batches
                                        if len(documents) % 10 == 0:
                                            batch_embeddings = embedding_model.encode(documents[-10:]).tolist()
                                            embeddings.extend(batch_embeddings)
                                        
                                        # Add to ChromaDB in batches
                                        if len(documents) % 50 == 0:
                                            collection.add(
                                                documents=documents[-50:],
                                                embeddings=embeddings[-50:],
                                                metadatas=metadatas[-50:],
                                                ids=ids[-50:]
                                            )
                                            print(f"Added {len(documents)} chunks from {filename}")
                                        
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
        
        # Add any remaining documents
        if documents:
            remaining_embeddings = embedding_model.encode(documents).tolist()
            collection.add(
                documents=documents,
                embeddings=remaining_embeddings,
                metadatas=metadatas,
                ids=ids
            )
        
        print(f"Successfully ingested {len(documents)} chunks into ChromaDB")
        return True
        
    except Exception as e:
        print(f"Error ingesting documents: {e}")
        return False

def get_simple_context(query):
    """Get simple context based on keywords instead of embeddings."""
    # This is a simplified version that doesn't require sentence-transformers
    # In a real deployment, you'd want to add back the embedding functionality
    return "Sample textbook context for Tax Court exam preparation."

def check_answer_with_openai(question_text, user_answer, context_chunks=None, model='gpt-3.5-turbo'):
    """Check student answer using OpenAI."""
    client = setup_openai_client()
    if client is None:
        return "Error: OpenAI API key not configured. Please check your .env file."
    
    # Try to get relevant chunks from ChromaDB
    context_chunks = retrieve_relevant_chunks(question_text)
    
    if context_chunks:
        context = "\n\n".join([
            f"From {meta.get('filename', 'Unknown')} (page {meta.get('page', 'Unknown')}):\n{chunk}"
            for chunk, meta in context_chunks
        ])
    else:
        context = get_simple_context(question_text)
    
    system_prompt = """You are Miles's enthusiastic and encouraging Tax Court Exam Prep Buddy! Your role is to:

1. Help Miles prepare for the Tax Court exam with enthusiasm and positivity
2. Evaluate his answers to practice questions with constructive, encouraging feedback
3. Cite relevant textbook sources when possible
4. Use warm, motivating language that builds confidence
5. If an answer is incorrect, provide the correct answer with clear explanation while maintaining encouragement
6. Remember that Miles is studying for the Tax Court exam specifically, so focus on tax law, court procedures, and relevant legal concepts
7. Be supportive and remind Miles that learning is a process - every question is an opportunity to improve
8. Use phrases like "Great effort!", "You're on the right track!", "Excellent thinking!", and "Keep up the great work!"

Remember: You're not just a tutor, you're Miles's study buddy and cheerleader!"""

    user_prompt = f"""Practice Question: {question_text}

Student's Answer: {user_answer}

Textbook Excerpts:
{context}

Please provide feedback on the student's answer. Include:
- Whether the answer is correct
- What was good about their answer (if anything)
- What needs improvement
- The correct answer with explanation
- Citations to relevant textbook sources"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

@app.route('/')
def index():
    """Main page with practice interface."""
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    """Get available practice questions."""
    questions = load_questions_from_folder(questions_folder)
    return jsonify({
        'questions': questions,
        'count': len(questions)
    })

@app.route('/api/random-question')
def get_random_question():
    """Get a random practice question."""
    questions = load_questions_from_folder(questions_folder)
    if not questions:
        # Return a sample question if no PDFs are found
        sample_question = {
            'text': "What is the primary purpose of the Tax Court in the United States?",
            'source': 'Sample Question'
        }
        return jsonify(sample_question)
    
    question = random.choice(questions)
    return jsonify(question)

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    """Check a student's answer."""
    data = request.get_json()
    question_text = data.get('question')
    user_answer = data.get('answer')
    
    if not question_text or not user_answer:
        return jsonify({'error': 'Question and answer are required'}), 400
    
    # Get feedback from OpenAI
    feedback = check_answer_with_openai(question_text, user_answer)
    
    # Get context sources from chunks
    context_sources = []
    if context_chunks:
        context_sources = [f"{meta.get('filename', 'Unknown')} (page {meta.get('page', 'Unknown')})" 
                          for _, meta in context_chunks]
    else:
        context_sources = ['Sample Textbook']
    
    return jsonify({
        'feedback': feedback,
        'context_sources': context_sources
    })

@app.route('/api/ingest-documents', methods=['POST'])
def ingest_documents():
    """Ingest textbook documents into ChromaDB."""
    try:
        success = ingest_documents_to_chromadb()
        if success:
            return jsonify({'message': 'Documents successfully ingested into ChromaDB'})
        else:
            return jsonify({'error': 'Failed to ingest documents'}), 500
    except Exception as e:
        return jsonify({'error': f'Error ingesting documents: {str(e)}'}), 500

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Ask a custom question and get an answer."""
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Get answer from OpenAI
    client = setup_openai_client()
    if client is None:
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    # Try to get relevant chunks from ChromaDB
    context_chunks = retrieve_relevant_chunks(question)
    
    if context_chunks:
        context = "\n\n".join([
            f"From {meta.get('filename', 'Unknown')} (page {meta.get('page', 'Unknown')}):\n{chunk}"
            for chunk, meta in context_chunks
        ])
    else:
        context = get_simple_context(question)
    
    system_prompt = """You are Miles's enthusiastic and encouraging Tax Court Exam Prep Buddy! Use the provided textbook excerpts to answer questions accurately and comprehensively.

Your role is to:
1. Help Miles understand Tax Court exam concepts with enthusiasm and clarity
2. Use warm, encouraging language that builds his confidence
3. Focus on tax law, court procedures, and relevant legal concepts for the Tax Court exam
4. If the context doesn't contain enough information, say so clearly but encouragingly
5. Always cite the source (filename and page) when possible
6. Use phrases like "Great question!", "Here's what you need to know for the Tax Court exam...", and "This is important for your exam prep!"

Remember: You're Miles's study buddy and cheerleader - be enthusiastic and supportive!"""
    
    user_prompt = f"""Use the following textbook excerpts to answer the question.

Context:
{context}

Question: {question}

Please provide a clear, accurate answer based on the context provided."""

    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        answer = response.choices[0].message.content.strip()
        
        # Get context sources from chunks
        context_sources = []
        if context_chunks:
            context_sources = [f"{meta.get('filename', 'Unknown')} (page {meta.get('page', 'Unknown')})" 
                              for _, meta in context_chunks]
        else:
            context_sources = ['Sample Textbook']
        
        return jsonify({
            'answer': answer,
            'context_sources': context_sources
        })
    except Exception as e:
        return jsonify({'error': f'Error calling OpenAI API: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 