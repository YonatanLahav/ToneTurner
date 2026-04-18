# 🎭 ToneTurner

Multi-Tone AI Rephrasing Application - Transform your text into multiple communication styles instantly.

## Features

- **Single Input, Multi-Output**: Generate 4 tone variations from one input
- **Blazing Fast**: Powered by Groq (Llama 3.3 70B) for ultra-fast responses
- **Hebrew → English**: Automatic Hebrew detection and translation
- **Output Length Control**: 5-level slider from Very Concise to Very Detailed
- **Custom Instructions**: Add your own style tweaks (formal, humorous, etc.)
- **Dark Mode**: Toggle light/dark themes
- **Structured Output**: Reliable JSON-based responses
- **Clean UI**: 2x2 grid comparison layout
- **Easy Copy**: One-click copy to clipboard

## Tones Available

1. **Professional** 💼 - Clear, polite, workplace-appropriate
2. **Friendly** 😊 - Warm, approachable, casual
3. **Direct** 🎯 - Concise, straight to the point
4. **Creative** ✨ - Unique, engaging, stylized

## Installation

1. Clone the repository:
```bash
cd toneturner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Groq API key:

   **Option 1: Using .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

   **Option 2: Using Streamlit secrets**
   ```bash
   mkdir -p .streamlit
   echo 'GROQ_API_KEY = "your_key_here"' > .streamlit/secrets.toml
   ```

## Getting a Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or sign in
3. Navigate to API Keys section
4. Click "Create API Key"
5. Copy the key and add it to your `.env` or `.streamlit/secrets.toml`

## Usage

Run the application:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
toneturner/
├── app.py                      # Main Streamlit application
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration settings
│   ├── services/
│   │   ├── __init__.py
│   │   └── groq_service.py     # Groq API integration
│   └── components/
│       ├── __init__.py
│       └── ui_components.py    # UI rendering components
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development Roadmap

### Phase 1: MVP ✅
- [x] Groq API integration
- [x] JSON parsing
- [x] 2x2 grid layout
- [x] Basic UI components

### Phase 2: UX Enhancement ✅
- [x] Copy to clipboard functionality
- [x] Custom tone field
- [x] Dark/light mode toggle
- [x] Output length slider
- [x] Hebrew → English auto-translation

### Phase 3: Advanced Features
- [ ] Context-aware rephrasing (Email vs Slack vs LinkedIn)
- [ ] Rephrase history panel
- [ ] User authentication
- [ ] Database integration (Supabase)
- [ ] Batch mode (CSV upload)

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Groq (Llama 3.3 70B Versatile)
- **Language**: Python 3.8+
- **Deployment**: Streamlit Cloud / Vercel

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
