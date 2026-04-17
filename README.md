# 🎭 ToneTurner

Multi-Tone AI Rephrasing Application - Transform your text into multiple communication styles instantly.

## Features

- **Single Input, Multi-Output**: Generate 4 tone variations from one input
- **Fast & Efficient**: Powered by Gemini 1.5 Flash for sub-2-second responses
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

4. Set up your Gemini API key:

   **Option 1: Using .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

   **Option 2: Using Streamlit secrets**
   ```bash
   mkdir -p .streamlit
   echo 'GEMINI_API_KEY = "your_key_here"' > .streamlit/secrets.toml
   ```

## Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` or `.streamlit/secrets.toml`

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
│   │   └── gemini_service.py   # Gemini API integration
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
- [x] Gemini API integration
- [x] JSON parsing
- [x] 2x2 grid layout
- [x] Basic UI components

### Phase 2: UX Enhancement
- [ ] Copy to clipboard functionality
- [ ] Custom tone field
- [ ] Dark/light mode toggle
- [ ] Output length slider

### Phase 3: Advanced Features
- [ ] Context-aware rephrasing (Email vs Slack)
- [ ] User authentication
- [ ] Rephrase history
- [ ] Database integration (Supabase)

## Technology Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 1.5 Flash
- **Language**: Python 3.8+
- **Deployment**: Streamlit Cloud / Vercel

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
