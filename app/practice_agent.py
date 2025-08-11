import pdfplumber
import os
import random
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import re

# Set up project-root-relative persist directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
persist_dir = os.path.join(project_root, "db", "chroma_db_test")
os.makedirs(persist_dir, exist_ok=True)

# Connect to ChromaDB
chroma_client = chromadb.PersistentClient(path=persist_dir)
collection = chroma_client.get_or_create_collection("textbook_chunks")

# Load the embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

import re

def load_questions_from_folder(folder_path):
    import re
    questions = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
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
    return questions

def retrieve_relevant_chunks(query, top_k=5):
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

def check_answer_with_llm(question_text, user_answer, context_chunks, model='llama2'):
    context = "\n\n".join([
        f"From {meta['filename']} (page {meta['page']}):\n{chunk}"
        for chunk, meta in context_chunks
    ])
    prompt = (
        f"You are a helpful CPA study assistant. "
        f"Here is a practice question and a student's answer. "
        f"Use the provided textbook excerpts to check the answer. "
        f"If the answer is correct, say so. If not, provide the correct answer and cite the relevant textbook sources.\n\n"
        f"Practice Question: {question_text}\n"
        f"Student's Answer: {user_answer}\n\n"
        f"Textbook Excerpts:\n{context}\n"
        f"Your feedback (with citations):"
    )
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful CPA study assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content'].strip()

if __name__ == "__main__":
    questions = load_questions_from_folder(os.path.join(project_root, 'data', 'questions'))

    #PRACTICE LOOP Export to text file
   # with open('extracted_questions.txt', 'w', encoding='utf-8') as f:
   #     for q in questions:
   #         f.write(q['text'] + '\n\n')

    # Comment out the practice loop for now
    # random.shuffle(questions)
    # for question in questions:
    #     ...

if __name__ == "__main__":
    questions = load_questions_from_folder(os.path.join(project_root, 'data', 'questions'))
    random.shuffle(questions)
    for question in questions:
        print("\nPractice Question:")
        print(question['text'])
        user_answer = input("Your answer: ")
        context_chunks = retrieve_relevant_chunks(question['text'], top_k=3)
        feedback = check_answer_with_llm(question['text'], user_answer, context_chunks, model='mistral')
        print("\nFeedback:\n", feedback)
        # Optionally, break after one for testing
        break