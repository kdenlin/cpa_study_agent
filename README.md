---
title: CPA Study Agent - Tax Court Exam Prep Buddy
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 3.50.2
app_file: gradio_app.py
pinned: false
---

# CPA Study Agent - Tax Court Exam Prep Buddy

An AI-powered study assistant for Tax Court exam preparation using Flask, OpenAI, and ChromaDB.

## Features

- Practice question generation and evaluation
- Textbook document ingestion and retrieval
- AI-powered answer checking with feedback
- Custom question asking with context-aware responses
- ChromaDB for document storage and retrieval

## Deployment to Hugging Face Spaces

### Prerequisites
1. A Hugging Face account
2. OpenAI API key

### Steps to Deploy

1. **Create a Hugging Face Space:**
   - Go to [Hugging Face Spaces](https://huggingface.co/spaces)
   - Click "Create new Space"
   - Choose "Gradio" as the SDK
   - Name your space (e.g., "cpa-study-agent")
   - Choose public or private

2. **Clone your space repository:**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   cd YOUR_SPACE_NAME
   ```

3. **Copy your application files:**
   - Copy all files from this directory to your space repository
   - Make sure to include: `app.py`, `requirements.txt`, `templates/`, etc.

4. **Set up environment variables:**
   - In your Hugging Face Space settings, add:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `FLASK_ENV`: "production"

5. **Push to deploy:**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

## Usage

1. **Practice Questions:** Get random practice questions and submit answers for AI feedback
2. **Document Ingestion:** Upload textbook PDFs to build a knowledge base
3. **Custom Questions:** Ask specific questions and get context-aware answers
4. **Answer Checking:** Submit answers to practice questions for detailed feedback

## File Structure

- `app.py`: Main Flask application
- `requirements.txt`: Python dependencies
- `templates/`: HTML templates
- `data/`: Directory for questions and textbooks
- `db/`: ChromaDB storage directory

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_ENV`: Flask environment (production/development)
- `PORT`: Port number (default: 5000) 