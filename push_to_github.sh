#!/bin/bash

# Script to push ClassIQ to GitHub
# This will authenticate you with GitHub and create the repository

echo "🚀 Setting up GitHub repository for ClassIQ..."
echo ""

# Check if already authenticated
if gh auth status &>/dev/null; then
    echo "✅ Already authenticated with GitHub"
else
    echo "📝 You need to authenticate with GitHub first"
    echo "   This will open a browser window for authentication"
    echo ""
    gh auth login
fi

echo ""
echo "📦 Creating GitHub repository and pushing code..."
echo ""

# Create repository and push
gh repo create classiq \
    --public \
    --source=. \
    --remote=origin \
    --description="AI-Powered Classroom Assistant - Full-stack web application for automated grading and analytics" \
    --push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    gh repo view --web
else
    echo ""
    echo "❌ Failed to push. Please check the error messages above."
fi

