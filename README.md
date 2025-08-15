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

An AI-powered chatbot for Tax Court exam preparation using OpenAI GPT and ChromaDB for document retrieval.

## Features

- **AI-Powered Q&A**: Ask questions about Tax Court exam topics and get detailed answers
- **Document Retrieval**: Uses ChromaDB to find relevant textbook excerpts
- **Practice Questions**: Access to past exam questions and practice materials
- **Web Interface**: Clean, responsive web interface built with Flask

## Quick Start

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
4. Run the application: `python app.py`
5. Open http://localhost:7860 in your browser

### Hugging Face Spaces Deployment

1. **Fork this repository** to your Hugging Face account
2. **Add your OpenAI API key as a secret**:
   - Go to your repository settings
   - Navigate to "Secrets and variables" > "Actions"
   - Click "New repository secret"
   - Name: `OPENAI_API_KEY`
   - Value: Your actual OpenAI API key (starts with `sk-` or `sk-proj-`)
3. **Wait for deployment** - Hugging Face will automatically build and deploy your app
4. **Access your app** at: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_REPO_NAME`

## Troubleshooting

### "OpenAI API key not configured" Error

If you see this error on Hugging Face Spaces:

1. **Check your secret name**: Make sure it's exactly `OPENAI_API_KEY` (case sensitive)
2. **Verify the secret value**: Ensure it's your actual API key, not a placeholder
3. **Wait for redeployment**: After adding the secret, wait 2-3 minutes for the app to redeploy
4. **Check the logs**: Go to the "Logs" tab in your Hugging Face Space to see detailed error messages

### API Key Format

Your OpenAI API key should:
- Start with `sk-` (standard key) or `sk-proj-` (project key)
- Be 51+ characters long
- Not contain any extra spaces or quotes

### Common Issues

- **"API key not found"**: Make sure you added the secret to the correct repository
- **"Invalid API key"**: Check that your key is valid and has sufficient credits
- **"Deployment failed"**: Check the Actions tab for build errors

## Project Structure

```
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/
│   ├── questions/           # PDF files with practice questions
│   └── textbooks/           # PDF files with textbook content
├── db/                      # ChromaDB database (auto-created)
└── templates/
    └── index.html           # Web interface
```

## Dependencies

- Flask (web framework)
- OpenAI (AI API)
- ChromaDB (vector database)
- pdfplumber (PDF processing)
- python-dotenv (environment variables)

## License

This project is for educational purposes. Please ensure you comply with OpenAI's usage policies. 