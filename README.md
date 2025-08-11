# Miles's Tax Court Exam Prep Buddy

A modern, AI-powered web application for Tax Court exam preparation. This application provides practice questions, AI-powered feedback, and a knowledge base built from your study materials, all with enthusiastic encouragement for Miles's exam prep journey.

## Features

- **Practice Questions**: Get random practice questions from your study materials
- **AI Feedback**: Receive detailed feedback on your answers using OpenAI
- **Custom Questions**: Ask any CPA-related question and get answers from your textbooks
- **Modern Interface**: Clean, professional web interface that works on all devices
- **Knowledge Base**: Built from your textbook materials using advanced RAG (Retrieval-Augmented Generation)

## Quick Start

### 1. Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API Key:**
   - Edit the `.env` file
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   - Get your API key from: https://platform.openai.com/api-keys

3. **Add Practice Questions:**
   - Place your practice question PDFs in the `data/questions/` folder
   - The app will automatically extract questions from these files

### 2. Run the Application

```bash
python run_app.py
```

The application will be available at: **http://localhost:5000**

## How to Use

### For Miles (Your Boss)

1. **Open the web browser** and go to `http://localhost:5000`

2. **Tax Court Practice Questions Tab:**
   - Click "New Question" to get a random Tax Court practice question
   - Type your answer in the text box
   - Click "Check Answer" to get enthusiastic, encouraging feedback
   - The feedback will include what you got right, what needs improvement, and the correct answer with motivation

3. **Ask Tax Court Questions Tab:**
   - Type any Tax Court or tax law question you have
   - Click "Ask Question" to get an enthusiastic answer based on your study materials
   - The answer will include citations to relevant textbook sources

4. **Tax Court Study Progress Tab:**
   - View how many practice questions are available
   - See the status of your knowledge base

### Features for Easy Use

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Keyboard Shortcuts**: 
  - `Ctrl+Enter` in answer boxes to submit
- **Loading Indicators**: Clear feedback when processing requests
- **Error Handling**: Helpful error messages if something goes wrong

## File Structure

```
cpa_study_agent/
├── app.py                 # Main Flask application
├── run_app.py            # Startup script with setup checks
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (API keys)
├── templates/
│   └── index.html       # Web interface
├── data/
│   └── questions/       # Practice question PDFs
└── app/
    ├── db/              # ChromaDB database
    └── rag/             # RAG implementation
```

## Technical Details

### AI Models Used
- **OpenAI GPT-3.5-turbo**: For answering questions and providing feedback
- **Sentence Transformers**: For semantic search and retrieval
- **ChromaDB**: Vector database for storing and retrieving relevant content

### API Endpoints
- `GET /api/questions`: Get all available practice questions
- `GET /api/random-question`: Get a random practice question
- `POST /api/check-answer`: Check a student's answer
- `POST /api/ask-question`: Ask a custom question

## Troubleshooting

### Common Issues

1. **"OpenAI API key not configured"**
   - Make sure you've updated the `.env` file with your actual API key
   - Check that the API key starts with `sk-`

2. **"No questions found"**
   - Make sure you have PDF files in the `data/questions/` folder
   - Check that the PDFs contain practice questions in the expected format

3. **"Error calling OpenAI API"**
   - Verify your API key is valid and has sufficient credits
   - Check your internet connection

4. **Application won't start**
   - Run `pip install -r requirements.txt` to install dependencies
   - Make sure you're in the correct directory

### Getting Help

If you encounter any issues:
1. Check the console output for error messages
2. Verify your OpenAI API key is working
3. Make sure all required files are in place

## Security Notes

- The `.env` file contains your API key - keep it secure
- The application runs locally on your machine
- No data is sent to external servers except OpenAI API calls

## Future Enhancements

- User progress tracking
- Question difficulty levels
- Study session timers
- Export practice results
- Integration with more study materials

---

**Happy Studying! 🎓** 