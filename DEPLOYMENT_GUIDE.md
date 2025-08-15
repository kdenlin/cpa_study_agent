# CPA Study Agent - Hugging Face Spaces Deployment Guide

This guide will help you deploy your CPA Study Agent to Hugging Face Spaces and fix the OpenAI API key configuration issue.

## Quick Fix for "OpenAI API key not configured" Error

If you're seeing this error, follow these steps:

### 1. Add OpenAI API Key to Repository Secrets

1. **Go to your Hugging Face repository**
   - Navigate to your CPA Study Agent repository on Hugging Face

2. **Access repository settings**
   - Click on the **Settings** tab in your repository

3. **Navigate to secrets**
   - In the left sidebar, click **Secrets and variables** > **Actions**

4. **Add new repository secret**
   - Click **New repository secret**
   - Set the name to: `OPENAI_API_KEY` (exactly this, case sensitive)
   - Set the value to your actual OpenAI API key
   - Click **Add secret**

### 2. Verify Your API Key Format

Your OpenAI API key should:
- Start with `sk-` (standard key) or `sk-proj-` (project key)
- Be 51+ characters long
- Not contain any extra spaces, quotes, or special characters

### 3. Wait for Redeployment

After adding the secret:
- Hugging Face will automatically trigger a new deployment
- Wait 2-3 minutes for the deployment to complete
- Check the **Actions** tab to see deployment progress

### 4. Test Your Deployment

Once deployed, your app should be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/YOUR_REPO_NAME
```

## Detailed Troubleshooting

### If the error persists:

1. **Check the secret name**
   - Make sure it's exactly `OPENAI_API_KEY` (case sensitive)
   - No extra spaces or characters

2. **Verify the secret value**
   - Ensure it's your actual API key, not a placeholder
   - Check that it starts with `sk-` or `sk-proj-`

3. **Check deployment logs**
   - Go to the **Logs** tab in your Hugging Face Space
   - Look for any error messages related to the API key

4. **Test locally first**
   - Run the test script: `python test_huggingface_deployment.py`
   - This will help identify if the issue is with your API key or the deployment

### Common Issues and Solutions

#### Issue: "API key not found"
**Solution**: Make sure you added the secret to the correct repository and with the exact name `OPENAI_API_KEY`

#### Issue: "Invalid API key"
**Solution**: 
- Check that your API key is valid and has sufficient credits
- Verify the key format (should start with `sk-` or `sk-proj-`)
- Make sure there are no extra characters or spaces

#### Issue: "Deployment failed"
**Solution**:
- Check the **Actions** tab for build errors
- Ensure all required files are in the repository
- Verify that `requirements.txt` contains all necessary dependencies

## Required Files for Deployment

Make sure these files are in your repository:

```
├── app.py                           # Main Flask application
├── requirements.txt                 # Python dependencies
├── README.md                        # Project description
├── huggingface_spaces_config.py     # Hugging Face configuration
├── test_huggingface_deployment.py   # Deployment test script
├── data/
│   ├── questions/                   # PDF files with practice questions
│   └── textbooks/                   # PDF files with textbook content
├── db/                              # ChromaDB database (auto-created)
└── templates/
    └── index.html                   # Web interface
```

## Testing Your Deployment

### Before deploying to Hugging Face:

1. **Test locally**:
   ```bash
   python test_huggingface_deployment.py
   ```

2. **Test the main app**:
   ```bash
   python app.py
   ```

### After deployment:

1. **Check the logs** in your Hugging Face Space
2. **Test the web interface** by asking a question
3. **Monitor API usage** in your OpenAI dashboard

## Environment Variables

The application automatically detects environment variables from:
- `.env` file (local development)
- Hugging Face Spaces secrets (production)

No additional configuration is needed.

## Support

If you continue to have issues:

1. **Check the logs** in your Hugging Face Space
2. **Run the test script** locally to verify your setup
3. **Verify your API key** is valid and has sufficient credits
4. **Ensure all dependencies** are listed in `requirements.txt`

## Monitoring

- **Logs**: Check the **Logs** tab for application output
- **Metrics**: Monitor performance in the **Metrics** tab
- **API Usage**: Track usage in your OpenAI dashboard
- **Actions**: Monitor deployment status in the **Actions** tab 