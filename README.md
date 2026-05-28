# 🤖 BotNLP — Intelligent Chatbot with NLP & Web UI

A Python chatbot with NLP intent detection, conversation memory, and a Flask web interface. Uses spaCy for NLP and supports free LLM backends (Groq, Ollama, Gemini).

---

## Features

- **NLP Intent Detection** — spaCy lemmatization + NLTK tokenization + fuzzy scoring
- **Named Entity Recognition** — extracts names, places, dates from user input
- **Conversation Memory** — remembers history, context, and last intent per session
- **AI Fallback** — routes unknown queries to a free LLM (Groq / Ollama / Gemini)
- **Flask Web UI** — clean chat interface with typing indicator and NLP metadata
- **Multi-session support** — each browser tab gets its own independent bot instance

---

## Project Structure

```
chatbot/
├── app.py              # Flask server & session management
├── chatbot.py          # Core NLP logic + intent detection
├── memory.py           # Conversation memory & context store
├── intents.json        # Intent definitions (patterns + responses)
├── templates/
│   └── index.html      # Chat web UI
├── .env                # Your secret keys (never commit this)
├── .env.example        # Template showing required variables
├── .gitignore
└── requirements.txt
```

---

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/botnlp.git
cd botnlp
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Then download NLTK data once:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

The chatbot uses a rule-based system first. For unknown queries, it falls back to:

### Groq 

1. Sign up at [console.groq.com](https://console.groq.com) — no credit card needed
2. Create an API key
3. Add to `.env`:

```
GROQ_API_KEY=your_key_here
```

## How Intent Detection Works

```
User input
   │
   ▼
NLP preprocessing (spaCy lemmatize + NLTK stopword removal)
   │
   ▼
Intent scoring
  1. Exact substring match → confidence 1.0
  2. Token overlap score
  3. Fuzzy string similarity (difflib)
   │
   ├── confidence ≥ 0.25 → Rule-based response from intents.json
   │
   └── confidence < 0.25 → AI fallback (Groq / Ollama / Gemini)
                                  + last 3 turns of memory as context
```

---

## Adding New Intents

Edit `intents.json` — no code changes needed:

```json
{
  "tag": "your_intent_name",
  "patterns": ["phrase 1", "phrase 2", "another way to say it"],
  "responses": ["Response option 1", "Response option 2"]
}
```

The bot randomly picks from `responses` each time the intent is matched.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the chat UI |
| POST | `/chat` | Send a message, get a response |
| POST | `/reset` | Clear conversation memory for the session |

### POST `/chat`

Request:
```json
{ "message": "hello" }
```

Response:
```json
{
  "response": "Hey there!",
  "intent": "greeting",
  "confidence": 1.0,
  "entities": {},
  "history": [...]
}
```

---

## Requirements

```
flask
spacy
nltk
python-dotenv
groq              
```

Install all:

```bash
pip install -r requirements.txt
```
