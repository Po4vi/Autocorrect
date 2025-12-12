# 🤔 Think - AI Spell-Check Chatbot

A modern, intelligent spell-checking chatbot powered by OpenRouter APIs with a ChatGPT-style interface.

## Features

✨ **Smart Features**
- **Dual-Mode Intelligence**: Separates spell-checking analysis from natural conversation
- **Real-time Spell Checking**: Levenshtein distance algorithm with smart suggestions
- **AI-Powered Responses**: OpenAI GPT-3.5-Turbo via OpenRouter
- **Conversation Memory**: Session-based history (up to 50 messages)
- **Beautiful UI**: ChatGPT-style interface with message avatars and analysis cards
- **Interactive Corrections**: Click to accept suggestions or apply full corrections
- **Copy to Clipboard**: Easy sharing of corrected text

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **OpenRouter API Key** - [Get free API key](https://openrouter.ai/)

## Local Setup

### 1. Clone Repository
```bash
git clone https://github.com/Po4vi/Autocorrect.git
cd Autocorrect
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
```bash
OPENROUTER_API_KEY=your_actual_api_key_here
PORT=5000
```

**Get your API key:**
1. Go to [openrouter.ai](https://openrouter.ai/)
2. Sign up (free account)
3. Navigate to Keys section
4. Create new API key
5. Copy and paste into `.env`

### 5. Run the Server
```bash
python server.py
```

The server will run on `http://localhost:5000`

## Deployment

### Option 1: Render (Recommended - Free)

1. **Create Render Account**
   - Go to [render.com](https://render.com/)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `Autocorrect` repo

3. **Configure Service**
   ```
   Name: think-chatbot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python server.py
   ```

4. **Add Environment Variables**
   - Go to "Environment" tab
   - Add: `OPENROUTER_API_KEY` = your_key
   - Add: `PORT` = 5000

5. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Access your app at: `https://think-chatbot.onrender.com`

### Option 2: Railway

1. **Setup**
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   ```

2. **Deploy**
   ```bash
   railway init
   railway up
   ```

3. **Add Environment Variables**
   ```bash
   railway variables set OPENROUTER_API_KEY=your_key
   railway variables set PORT=5000
   ```

4. **Generate Domain**
   ```bash
   railway domain
   ```

### Option 3: PythonAnywhere

1. **Create Account** at [pythonanywhere.com](https://www.pythonanywhere.com/)

2. **Upload Code**
   - Go to "Files" tab
   - Upload all project files

3. **Setup Virtual Environment**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to "Web" tab → "Add a new web app"
   - Select "Manual configuration" → Python 3.10
   - Set source code directory: `/home/yourusername/Autocorrect`
   - Edit WSGI file to point to `server.py`

5. **Set Environment Variables**
   - Add to WSGI file or use `.env`

6. **Reload** and visit your domain

### Option 4: DigitalOcean App Platform

1. **Create Account** at [digitalocean.com](https://www.digitalocean.com/)

2. **Create App**
   - Click "Create" → "Apps"
   - Connect GitHub repository

3. **Configure**
   ```
   Type: Web Service
   Run Command: python server.py
   HTTP Port: 5000
   ```

4. **Add Environment Variables** in App settings

5. **Deploy** and access via provided URL

## Production Configuration

For production deployment, ensure:

1. **Set Production Host**
   ```python
   # In server.py, update the last line:
   app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
   ```

2. **Use Production WSGI Server**
   
   Add to `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```
   
   Update start command:
   ```bash
   gunicorn server:app --bind 0.0.0.0:$PORT
   ```

3. **Security Checklist**
   - ✅ Never commit `.env` file
   - ✅ Use environment variables for secrets
   - ✅ Enable HTTPS on your hosting platform
   - ✅ Set CORS origins properly for production
   - ✅ Monitor API usage and set rate limits

## How It Works

### Dual-Mode Intelligence

**Spell-Check Mode** (triggered by keywords: correct, fix, mistake, error, spell, grammar, check)
1. User types message with errors
2. Backend detects misspelled words using dictionary lookup
3. Levenshtein distance algorithm generates top 5 suggestions per error
4. AI provides natural response about the text
5. Frontend displays conversation + separate analysis card with error rows
6. User clicks suggestion chips to accept corrections

**Conversation Mode** (general questions)
1. User asks regular questions
2. Backend skips spell-checking logic
3. AI responds naturally like ChatGPT
4. No analysis cards shown, pure conversation flow

### Technical Flow

```
User Input → Flask Backend → Spell Check (Levenshtein) → OpenRouter API (GPT-3.5) 
→ Response + Errors → Frontend → ChatGPT-style UI → Interactive Corrections
```

## Technology Stack

**Backend:**
- Python 3.8+ with Flask
- OpenRouter API (OpenAI GPT-3.5-Turbo)
- Levenshtein Distance algorithm
- Session-based memory (UUID tracking)
- In-memory conversation storage (deque, maxlen=50)

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Modern CSS3 with gradients and animations
- Responsive design
- Clipboard API integration

## Project Structure

```
Autocorrect/
├── server.py              # Flask backend + spell-check logic
├── public/
│   └── index.html         # Frontend UI (ChatGPT-style)
├── dictionary.json        # English word dictionary (~100 words)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (gitignored)
├── .env.example          # Template for .env
├── .gitignore            # Git exclusions
└── README.md             # Documentation
```

## API Endpoints

**POST** `/api/chat`
- Send message, get AI response + spell errors
- Body: `{"message": "your text"}`
- Response: `{"response": "...", "spellingErrors": [...], "isSpellCheckMode": bool}`

**POST** `/api/accept-suggestion`
- Accept a spelling correction
- Body: `{"wrongWord": "...", "correctWord": "..."}`
- Response: `{"success": true}`

**POST** `/api/clear-history`
- Clear conversation history
- Response: `{"success": true}`

**GET** `/api/health`
- Health check endpoint
- Response: `{"status": "healthy"}`

### POST `/api/chat`
Sends a message and gets AI response with spell-check

**Request:**
```json
{
  "message": "i hav a speling error"
}
```

**Response:**
```json
{
  "message": "AI response explaining the corrections...",
  "spellingErrors": [
    {
      "word": "hav",
      "position": 2,
      "suggestions": ["have", "had", "haw"]
    },
    {
      "word": "speling",
      "position": 4,
      "suggestions": ["spelling", "spading", "spelding"]
    }
  ],
  "thinking": "Found 2 potential spelling error(s). Analyzing..."
}
```

### GET `/api/health`
Health check endpoint

## Customization

### Change AI Model
Edit `server.js` line 74:
```javascript
model: 'meta-llama/llama-2-70b-chat',  // Change this
```

### Expand Dictionary
Edit `dictionary.json` to add more words:
```json
[
  "existing_words",
  "your_new_words",
  "more_words"
]
```

### Modify System Prompt
Edit `server.js` line 78-88 to customize the AI behavior

### Adjust Temperature
Lower temperature (0.3) = More precise
Higher temperature (0.9) = More creative

## Troubleshooting

**"Invalid API Key"**
- Verify your OpenRouter API key in `.env`
- Make sure there are no extra spaces

**"Port already in use"**
```bash
# Use a different port in .env
PORT=3001
```

**"Cannot find module"**
```bash
npm install
```

## Features You Can Add

- [ ] Save chat history to database
- [ ] User authentication
- [ ] Grammar checking (not just spelling)
- [ ] Multiple languages support
- [ ] Context memory (remember previous messages)
- [ ] Custom dictionary per user
- [ ] Regex-based grammar patterns
- [ ] Integration with Grammarly API
- [ ] Typing effect for AI responses
- [ ] Message editing and re-generation

## Performance Tips

- Increase `max_tokens` for longer responses
- Reduce `temperature` for more consistent results
- Use smaller models for faster responses
- Cache common spelling corrections

## License

MIT

## Support

For issues or questions:
- Check `.env` configuration
- Verify OpenRouter API key is valid
- Check browser console for errors (F12)
- Check server logs in terminal

---

**Built with ❤️ using OpenRouter APIs**
