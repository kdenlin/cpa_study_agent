# Hugging Face Spaces Deployment Guide

## Setting up OpenAI API Key for Hugging Face Spaces

### 1. Add API Key to Repository Secrets

1. Go to your Hugging Face repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** > **Actions**
4. Click **New repository secret**
5. Set the name to: `OPENAI_API_KEY`
6. Set the value to your actual OpenAI API key
7. Click **Add secret**

### 2. Verify Your API Key Format

Your API key should start with either:
- `sk-` (standard OpenAI API key)
- `sk-proj-` (OpenAI project API key)

The error you're seeing suggests you have a `sk-proj-` key, which is now supported by the updated code.

### 3. Deploy Your Application

After adding the secret, your application should automatically redeploy. If not:

1. Go to the **Actions** tab in your repository
2. Look for any failed deployment workflows
3. Click on the failed workflow and check the logs for errors

### 4. Test the Deployment

Once deployed, your application should be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_REPO_NAME
```

### 5. Troubleshooting

#### Issue: "API key not configured" error persists
**Solution**: 
1. Make sure the secret name is exactly `OPENAI_API_KEY` (case sensitive)
2. Check that the secret value doesn't have extra spaces or quotes
3. Wait a few minutes for the deployment to complete

#### Issue: ChromaDB telemetry warnings
**Solution**: These are just warnings and don't affect functionality. The app should still work.

#### Issue: Application not loading
**Solution**:
1. Check the **Logs** tab in your Hugging Face Space
2. Look for any Python errors or missing dependencies
3. Make sure all required files are in the repository

### 6. Required Files for Hugging Face Spaces

Make sure these files are in your repository:

```
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                 # Project description
├── data/
│   ├── questions/           # PDF files with practice questions
│   └── textbooks/           # PDF files with textbook content
├── db/                      # ChromaDB database (will be created automatically)
└── templates/
    └── index.html           # Web interface
```

### 7. Environment Variables in Hugging Face Spaces

The application will automatically detect environment variables set through Hugging Face Spaces secrets. No additional configuration is needed.

### 8. Monitoring

- Check the **Logs** tab to see application output
- Monitor API usage in your OpenAI dashboard
- Check the **Metrics** tab for performance data

## Support

If you continue to have issues:
1. Check the **Logs** tab in your Hugging Face Space
2. Verify your API key is valid and has sufficient credits
3. Make sure all dependencies are listed in `requirements.txt`
