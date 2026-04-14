#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting setup for Clinical Intelligence RAG..."

# 1. Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 could not be found. Please install it to continue."
    exit 1
fi

# 2. Create Virtual Environment
echo "📦 Creating virtual environment (.venv)..."
python3 -m venv .venv

# 3. Activate Virtual Environment
source .venv/bin/activate

# 4. Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 5. Install Dependencies
echo "📥 Installing requirements from requirements.txt..."
pip install -r requirements.txt

# 6. Setup Environment File
if [ ! -f .env ]; then
    echo "📄 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Action Required: Update the .env file with your API keys!"
else
    echo "✅ .env file already exists."
fi

echo "--------------------------------------------------------"
echo "✅ Setup Complete!"
echo "💡 To start the application:"
echo "   1. Activate the environment: source .venv/bin/activate"
echo "   2. Run the server: uvicorn main:app --reload"
echo "--------------------------------------------------------"