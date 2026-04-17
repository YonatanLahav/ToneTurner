#!/bin/bash

# ToneTurner Setup Script

echo "🎭 Setting up ToneTurner..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Add your Gemini API key:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your API key"
echo ""
echo "2. Run the app:"
echo "   streamlit run app.py"
echo ""
echo "💡 To activate the virtual environment manually:"
echo "   source venv/bin/activate"
