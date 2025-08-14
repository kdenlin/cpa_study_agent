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

# CPA Study Agent

An AI-powered study assistant for Tax Court exam preparation, built with Flask and ChromaDB.

## Features

- **Practice Questions**: Get random practice questions and receive AI-powered feedback
- **Custom Questions**: Ask any question about Tax Court topics and get detailed answers
- **Document Management**: Ingest PDF textbooks and retrieve relevant information
- **Modern UI**: Clean, responsive web interface built with Bootstrap

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: ChromaDB (vector database for document storage)
- **AI**: OpenAI GPT-3.5-turbo for intelligent responses
- **Frontend**: Bootstrap 5 + jQuery for responsive UI
- **PDF Processing**: pdfplumber for text extraction
- **Embeddings**: sentence-transformers for semantic search

## Deployment

This application is configured for deployment on Hugging Face Spaces.

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## File Structure

```
cpa_study_agent/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── app.json              # Hugging Face Spaces configuration
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   └── index.html        # Main application interface
├── app/
│   └── ingestion/
│       └── pdf_ingest.py # PDF processing and ChromaDB ingestion
└── textbooks/            # Place PDF textbooks here
```

## API Endpoints

- `GET /` - Main application interface
- `GET /api/random-question` - Get a random practice question
- `POST /api/check-answer` - Check answer and get feedback
- `POST /api/ask-question` - Ask a custom question
- `POST /api/ingest-documents` - Ingest PDF documents
- `GET /api/ingest-status` - Check document ingestion status
- `POST /api/clear-database` - Clear the ChromaDB database

## Recent Changes

- **Converted from Gradio to pure Flask**: Eliminated dependency conflicts by removing Gradio
- **Modern UI**: Implemented responsive Bootstrap interface with tabbed navigation
- **Stable Dependencies**: Using older but stable versions of ChromaDB and Pydantic
- **Better Error Handling**: Improved error handling and user feedback

## Troubleshooting

If you encounter dependency issues:
1. The application uses ChromaDB 0.3.21 with Pydantic 1.10.13 for stability
2. All dependencies are pinned to specific versions to avoid conflicts
3. The Flask app runs directly without Gradio wrapper 