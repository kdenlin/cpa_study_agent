from flask import Flask, render_template, request, jsonify, session
import os
import random
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import pdfplumber
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Set up project paths
project_root = os.path.abspath(os.path.dirname(__file__))
persist_dir = os.path.join(project_root, "app", "db", "chroma_db_test")
questions_folder = os.path.join(project_root, "data", "questions")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=persist_dir)
collection = chroma_client.get_or_create_collection("textbook_chunks")

# Load the embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

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

def retrieve_relevant_chunks(query, top_k=5):
    """Retrieve relevant textbook chunks for a query."""
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas']
    )
    if not results or not results.get('documents') or not results['documents'] or not results['documents'][0]:
        return []
    if not results.get('metadatas') or not results['metadatas'] or not results['metadatas'][0]:
        return []
    return list(zip(results['documents'][0], results['metadatas'][0]))

def check_answer_with_openai(question_text, user_answer, context_chunks, model='gpt-3.5-turbo'):
    """Check student answer using OpenAI."""
    client = setup_openai_client()
    if client is None:
        return "Error: OpenAI API key not configured. Please check your .env file."
    
    context = "\n\n".join([
        f"From {meta['filename']} (page {meta['page']}):\n{chunk}"
        for chunk, meta in context_chunks
    ])
    
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
- Citations to relevant textbook sources, including page numbers where possible"""

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
        return jsonify({'error': 'No questions found'}), 404
    
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
    
    # Retrieve relevant context
    context_chunks = retrieve_relevant_chunks(question_text, top_k=3)
    
    # Get feedback from OpenAI
    feedback = check_answer_with_openai(question_text, user_answer, context_chunks)
    
    return jsonify({
        'feedback': feedback,
        'context_sources': [meta['filename'] for _, meta in context_chunks]
    })

@app.route('/api/ask-question', methods=['POST'])
def ask_question():
    """Ask a custom question and get an answer."""
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    # Retrieve relevant context
    context_chunks = retrieve_relevant_chunks(question, top_k=5)
    
    if not context_chunks:
        return jsonify({'error': 'No relevant information found'}), 404
    
    # Get answer from OpenAI
    client = setup_openai_client()
    if client is None:
        return jsonify({'error': 'OpenAI API key not configured'}), 500
    
    context = "\n\n".join([f"From {meta['filename']} (page {meta['page']}):\n{chunk}" for chunk, meta in context_chunks])
    
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
        
        return jsonify({
            'answer': answer,
            'context_sources': [meta['filename'] for _, meta in context_chunks]
        })
    except Exception as e:
        return jsonify({'error': f'Error calling OpenAI API: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 