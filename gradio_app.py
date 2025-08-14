#!/usr/bin/env python3
"""
Gradio wrapper for CPA Study Agent Flask app
This file makes the Flask app compatible with Hugging Face Spaces
"""

import gradio as gr
import requests
import json
import os
import threading
import time
from app import app

# Start Flask app in a separate thread
def start_flask_app():
    """Start the Flask app in a separate thread."""
    app.run(host='0.0.0.0', port=7861, debug=False, use_reloader=False)

# Start Flask app in background
flask_thread = threading.Thread(target=start_flask_app, daemon=True)
flask_thread.start()

# Wait a moment for Flask to start
time.sleep(2)

def create_gradio_interface():
    """Create a Gradio interface that communicates with the Flask app"""
    
    def get_random_question():
        """Get a random practice question"""
        try:
            response = requests.get("http://localhost:7861/api/random-question")
            if response.status_code == 200:
                question_data = response.json()
                return question_data.get('text', 'No question available')
            else:
                return "Error: Could not fetch question"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_answer(question, answer):
        """Check a student's answer"""
        try:
            response = requests.post("http://localhost:7861/api/check-answer", 
                                   json={'question': question, 'answer': answer})
            if response.status_code == 200:
                result = response.json()
                feedback = result.get('feedback', 'No feedback available')
                sources = result.get('context_sources', [])
                if sources:
                    feedback += f"\n\nSources: {', '.join(sources)}"
                return feedback
            else:
                return "Error: Could not check answer"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ask_custom_question(question):
        """Ask a custom question"""
        try:
            response = requests.post("http://localhost:7861/api/ask-question", 
                                   json={'question': question})
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer available')
                sources = result.get('context_sources', [])
                if sources:
                    answer += f"\n\nSources: {', '.join(sources)}"
                return answer
            else:
                return "Error: Could not get answer"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ingest_documents():
        """Ingest documents into ChromaDB"""
        try:
            response = requests.post("http://localhost:7861/api/ingest-documents")
            if response.status_code == 200:
                result = response.json()
                return result.get('message', 'Documents ingested successfully')
            else:
                result = response.json()
                return f"Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_database():
        """Clear the ChromaDB database"""
        try:
            response = requests.post("http://localhost:7861/api/clear-database")
            if response.status_code == 200:
                result = response.json()
                return result.get('message', 'Database cleared successfully')
            else:
                result = response.json()
                return f"Error: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_ingest_status():
        """Check document ingestion status"""
        try:
            response = requests.get("http://localhost:7861/api/ingest-status")
            if response.status_code == 200:
                result = response.json()
                chunks = result.get('chunks_ingested', 0)
                files = result.get('total_pdf_files', 0)
                return f"Status: {chunks} chunks ingested from {files} PDF files"
            else:
                return "Error: Could not check status"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Create Gradio interface
    with gr.Blocks(title="CPA Study Agent - Tax Court Exam Prep Buddy") as demo:
        gr.Markdown("# 📚 CPA Study Agent - Tax Court Exam Prep Buddy")
        gr.Markdown("Your AI-powered study assistant for Tax Court exam preparation!")
        
        with gr.Tab("Practice Questions"):
            with gr.Row():
                with gr.Column():
                    question_btn = gr.Button("Get Random Question", variant="primary")
                    question_text = gr.Textbox(label="Question", lines=5, interactive=False)
                    answer_input = gr.Textbox(label="Your Answer", lines=3, placeholder="Type your answer here...")
                    check_btn = gr.Button("Check Answer", variant="secondary")
                    feedback_output = gr.Textbox(label="Feedback", lines=10, interactive=False)
            
            question_btn.click(get_random_question, outputs=question_text)
            check_btn.click(check_answer, inputs=[question_text, answer_input], outputs=feedback_output)
        
        with gr.Tab("Ask Custom Question"):
            with gr.Row():
                with gr.Column():
                    custom_question = gr.Textbox(label="Ask a Question", lines=2, placeholder="What would you like to know about Tax Court?")
                    ask_btn = gr.Button("Ask Question", variant="primary")
                    custom_answer = gr.Textbox(label="Answer", lines=10, interactive=False)
            
            ask_btn.click(ask_custom_question, inputs=custom_question, outputs=custom_answer)
        
        with gr.Tab("Document Management"):
            with gr.Row():
                with gr.Column():
                    ingest_btn = gr.Button("Ingest Documents", variant="primary")
                    clear_btn = gr.Button("Clear Database", variant="secondary", size="sm")
                    status_btn = gr.Button("Check Status", variant="secondary")
                    status_output = gr.Textbox(label="Status", lines=3, interactive=False)
            
            ingest_btn.click(ingest_documents, outputs=status_output)
            clear_btn.click(clear_database, outputs=status_output)
            status_btn.click(check_ingest_status, outputs=status_output)
        
        with gr.Tab("About"):
            gr.Markdown("""
            ## About this Application
            
            This is an AI-powered study assistant designed to help you prepare for the Tax Court exam.
            
            **Features:**
            - Practice with randomly generated questions
            - Get detailed feedback on your answers
            - Ask custom questions about Tax Court topics
            - Document ingestion and retrieval with ChromaDB
            - AI-powered responses using OpenAI GPT-3.5-turbo
            
            **How to use:**
            1. Click "Get Random Question" to practice
            2. Type your answer and click "Check Answer"
            3. Use the "Ask Custom Question" tab for specific topics
            4. Use "Document Management" to ingest your PDF textbooks
            
            **Note:** Make sure to set your OpenAI API key in the environment variables.
            """)
    
    return demo

# Create and launch the interface
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860) 