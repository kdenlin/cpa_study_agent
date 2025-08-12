# Miles's Tax Court Exam Prep Buddy

An AI-powered study assistant for Tax Court exam preparation, built with Flask and OpenAI.

## Features

- 📚 **Document Ingestion**: Process PDF textbooks and extract questions
- 🤖 **AI-Powered Q&A**: Get answers using OpenAI GPT-3.5-turbo
- 🔍 **RAG System**: Retrieve relevant context from textbook chunks
- 💬 **Interactive Interface**: Web-based UI for easy interaction
- 📊 **Batch Processing**: Process large documents in manageable chunks

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-3.5-turbo
- **Vector Database**: ChromaDB
- **PDF Processing**: PDFPlumber
- **Deployment**: Hugging Face Spaces (Docker)

## Environment Variables

Set these in your Hugging Face Space settings:

- `OPENAI_API_KEY`: Your OpenAI API key

## Usage

1. **Access the web interface** at your Hugging Face Space URL
2. **Ingest documents** using the batch processing API
3. **Ask questions** and get AI-powered answers
4. **Practice with extracted questions** from your textbooks

## API Endpoints

- `GET /`: Main web interface
- `POST /api/ingest-batch`: Process PDF files in batches
- `GET /api/ingest-status`: Check ingestion status
- `POST /api/ask-question`: Ask custom questions
- `GET /api/random-question`: Get a random practice question
- `POST /api/check-answer`: Check answer accuracy

## Deployment

This app is configured for Hugging Face Spaces using Docker. The `Dockerfile` handles all dependencies and setup automatically. 