#!/usr/bin/env python3
"""
CPA Study Agent - Tax Court Exam Prep Buddy
Deployed on Hugging Face Spaces
"""

from flask import Flask, render_template, request, jsonify, session
import os
import random
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
import chromadb
from chromadb.config import Settings
import re
import threading
import time

# Load environment variables
load_dotenv()

# Disable ChromaDB telemetry to avoid warnings
os.environ["ANONYMIZED_TELEMETRY"] = "False"

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Set up project paths
project_root = os.path.abspath(os.path.dirname(__file__))
questions_folder = os.path.join(project_root, "data", "questions")
textbooks_folder = os.path.join(project_root, "textbooks")  # Changed from "data/textbooks" to "textbooks"
chroma_db_path = os.path.join(project_root, "db", "chroma_db_test")

def setup_openai_client():
    """Set up OpenAI client using environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        return None
    
    return OpenAI(api_key=api_key)

def setup_embedding_model():
    """Set up embedding model using ChromaDB's default."""
    try:
        # Use ChromaDB's default embedding function
        return None  # ChromaDB will use its default
    except Exception as e:
        print(f"Error setting up embedding model: {e}")
        return None

def setup_chroma_client():
    """Set up ChromaDB client."""
    try:
        client = chromadb.Client(chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=chroma_db_path
        ))
        return client
    except Exception as e:
        print(f"Error setting up ChromaDB: {e}")
        return None

def retrieve_relevant_chunks(query, n_results=3):
    """Retrieve relevant chunks from ChromaDB."""
    client = setup_chroma_client()
    
    if not client:
        return []
    
    try:
        # Get the collection (create if it doesn't exist)
        collection = client.get_or_create_collection("textbook_chunks")
        
        # Search for relevant chunks using text query (ChromaDB will handle embeddings)
        results = collection.query(
            query_texts=[query],
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

def load_questions_from_folder(folder_path):
    """Load practice questions from PDF files."""
    questions = []
    
    # First try to load from PDF files
    if os.path.exists(folder_path):
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
    
    # If no questions found from PDFs, load sample questions
    if not questions:
        sample_questions_path = os.path.join(project_root, "sample_questions.txt")
        if os.path.exists(sample_questions_path):
            try:
                with open(sample_questions_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Split by double newlines to get individual questions
                    question_blocks = content.split('\n\n')
                    for block in question_blocks:
                        if block.strip() and 'Question' in block:
                            questions.append({'text': block.strip(), 'source': 'Sample Questions'})
            except Exception as e:
                print(f"Error loading sample questions: {e}")
    
    # If still no questions, provide a default set
    if not questions:
        default_questions = [
            "What is the primary purpose of the Tax Court in the United States?",
            "What are the filing requirements for a petition to the Tax Court?",
            "Who bears the burden of proof in Tax Court proceedings?",
            "What are the Small Case Procedures in Tax Court?",
            "How does the appeals process work for Tax Court decisions?"
        ]
        for q in default_questions:
            questions.append({'text': q, 'source': 'Default Questions'})
    
    return questions

def ingest_documents_to_chromadb():
    """Ingest textbook documents into ChromaDB using the improved ingestion script."""
    try:
        # Import the improved ingestion function
        from app.ingestion.pdf_ingest import ingest_pdfs_to_chromadb
        return ingest_pdfs_to_chromadb()
    except Exception as e:
        print(f"Error importing or running ingestion script: {e}")
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
        return "Error: OpenAI API key not configured. Please check your environment variables."
    
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
    context_chunks = retrieve_relevant_chunks(question_text)
    if context_chunks:
        context_sources = [f"{meta.get('filename', 'Unknown')} (page {meta.get('page', 'Unknown')})" 
                          for _, meta in context_chunks]
    else:
        context_sources = ['Sample Textbook']
    
    return jsonify({
        'feedback': feedback,
        'context_sources': context_sources
    })

@app.route('/api/clear-database', methods=['POST'])
def clear_database():
    """Clear the ChromaDB collection and restart fresh."""
    try:
        client = setup_chroma_client()
        if not client:
            return jsonify({'error': 'ChromaDB not available'}), 500
        
        # Delete the existing collection
        try:
            client.delete_collection("textbook_chunks")
            print("Deleted existing collection")
        except:
            print("No existing collection to delete")
        
        # Create a fresh collection
        collection = client.create_collection("textbook_chunks")
        print("Created fresh collection")
        
        return jsonify({'message': 'Database cleared successfully. You can now re-ingest documents.'})
        
    except Exception as e:
        return jsonify({'error': f'Error clearing database: {str(e)}'}), 500

@app.route('/api/ingest-documents', methods=['POST'])
def ingest_documents():
    """Ingest textbook documents into ChromaDB."""
    try:
        print("Starting document ingestion...")
        print(f"Looking for PDFs in: {textbooks_folder}")
        print(f"Project root: {project_root}")
        
        # Check if textbooks folder exists
        if not os.path.exists(textbooks_folder):
            print(f"Textbooks folder does not exist: {textbooks_folder}")
            # Create the folder structure for future use
            os.makedirs(textbooks_folder, exist_ok=True)
            os.makedirs(questions_folder, exist_ok=True)
            
            error_msg = f"No PDF files found in textbooks folder. The folder has been created at: {textbooks_folder}"
            print(error_msg)
            return jsonify({
                'message': 'No PDF files found. Sample questions are available for practice.',
                'info': 'To add your own documents, upload PDF files to the textbooks folder.',
                'sample_available': True
            })
        
        # Check what files are in the folder
        files = os.listdir(textbooks_folder)
        print(f"All files in textbooks folder: {files}")
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files: {pdf_files}")
        
        if not pdf_files:
            # Also check the root directory for PDFs
            root_files = os.listdir(project_root)
            root_pdfs = [f for f in root_files if f.lower().endswith('.pdf')]
            print(f"Found {len(root_pdfs)} PDF files in root directory: {root_pdfs}")
            
            if root_pdfs:
                # Move PDFs to the textbooks folder
                for pdf_file in root_pdfs:
                    src_path = os.path.join(project_root, pdf_file)
                    dst_path = os.path.join(textbooks_folder, pdf_file)
                    try:
                        import shutil
                        shutil.copy2(src_path, dst_path)
                        print(f"Moved {pdf_file} to textbooks folder")
                    except Exception as e:
                        print(f"Error moving {pdf_file}: {e}")
                
                # Re-check the textbooks folder
                files = os.listdir(textbooks_folder)
                pdf_files = [f for f in files if f.lower().endswith('.pdf')]
                print(f"After moving, found {len(pdf_files)} PDF files: {pdf_files}")
            
            if not pdf_files:
                return jsonify({
                    'message': 'No PDF files found in the textbooks folder. Sample questions are available for practice.',
                    'info': 'To add your own documents, upload PDF files to the textbooks folder.',
                    'sample_available': True
                })
        
        success = ingest_documents_to_chromadb()
        if success:
            return jsonify({'message': f'Successfully processed {len(pdf_files)} PDF files into ChromaDB'})
        else:
            return jsonify({'error': 'Failed to ingest documents - check server logs'}), 500
    except Exception as e:
        error_msg = f'Error ingesting documents: {str(e)}'
        print(error_msg)
        return jsonify({'error': error_msg}), 500

@app.route('/api/ingest-status', methods=['GET'])
def ingest_status():
    """Check the status of document ingestion."""
    try:
        client = setup_chroma_client()
        if not client:
            return jsonify({'error': 'ChromaDB not available'}), 500
        
        collection = client.get_or_create_collection("textbook_chunks")
        chunk_count = collection.count()
        
        # Get list of PDF files from multiple locations
        files_info = {}
        
        # Check textbooks folder
        if os.path.exists(textbooks_folder):
            files = os.listdir(textbooks_folder)
            pdf_files = [f for f in files if f.lower().endswith('.pdf')]
            files_info['textbooks_folder'] = pdf_files
        else:
            files_info['textbooks_folder'] = []
        
        # Check root directory
        root_files = os.listdir(project_root)
        root_pdfs = [f for f in root_files if f.lower().endswith('.pdf')]
        files_info['root_directory'] = root_pdfs
        
        # Total PDF files found
        total_pdf_files = len(files_info['textbooks_folder']) + len(files_info['root_directory'])
        
        return jsonify({
            'chunks_ingested': chunk_count,
            'total_pdf_files': total_pdf_files,
            'has_data': chunk_count > 0,
            'files_info': files_info,
            'textbooks_folder_path': textbooks_folder,
            'root_directory_path': project_root
        })
        
    except Exception as e:
        return jsonify({'error': f'Error checking status: {str(e)}'}), 500

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

# Hugging Face Spaces specific configuration
app.config['PREFERRED_URL_SCHEME'] = 'https'

if __name__ == '__main__':
    # Hugging Face Spaces expects port 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port) 