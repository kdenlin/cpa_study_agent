# CPA Study Agent Setup Guide

## Environment Variables Setup

To fix the OpenAI API key issue, follow these steps:

### 1. Create a .env file

Create a file named `.env` in the `cpa_study_agent` directory (same folder as `app.py`) with the following content:

```
OPENAI_API_KEY=your_actual_api_key_here
```

Replace `your_actual_api_key_here` with your real OpenAI API key.

### 2. Get your OpenAI API key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in to your account
3. Go to "API Keys" in the left sidebar
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)

### 3. Test the setup

Run the debug script to verify everything is working:

```bash
python debug_api_key.py
```

### 4. Common Issues and Solutions

#### Issue: "API key found: Yes, starts with: sk-proj-Qc..."
**Solution**: This suggests you're using a different type of API key. Make sure you're using a standard OpenAI API key that starts with `sk-` (not `sk-proj-`).

#### Issue: "API key not configured"
**Solution**: 
1. Make sure the `.env` file is in the same directory as `app.py`
2. Make sure the `.env` file contains exactly: `OPENAI_API_KEY=your_key_here`
3. No spaces around the `=` sign
4. No quotes around the API key

#### Issue: "ChromaDB telemetry errors"
**Solution**: These are just warnings and don't affect functionality. The app should still work.

### 5. Folder Structure

The app expects this folder structure:
```
cpa_study_agent/
├── app.py
├── .env                    # Your API key goes here
├── data/
│   ├── questions/         # PDF files with practice questions
│   └── textbooks/         # PDF files with textbook content
├── db/
│   └── chroma_db_test/    # ChromaDB database files
└── templates/
    └── index.html
```

### 6. Running the Application

After setting up the `.env` file:

```bash
python app.py
```

The application should start without API key errors.

## Troubleshooting

If you're still having issues:

1. **Run the debug script**: `python debug_api_key.py`
2. **Check file permissions**: Make sure the `.env` file is readable
3. **Restart the application**: Sometimes environment variables need a restart to load
4. **Check for typos**: Make sure there are no extra spaces or characters in the `.env` file

## Support

If you continue to have issues, check:
- The debug output from `debug_api_key.py`
- The console output when running `app.py`
- That your OpenAI API key is valid and has sufficient credits
