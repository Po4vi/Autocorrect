# 🤔 Think - AI Spell-Check Chatbot

A modern, intelligent spell-checking chatbot powered by OpenRouter APIs with a beautiful web interface.

## Features

✨ **Smart Features**
- Real-time spell checking with AI-powered corrections
- OpenRouter API integration (supports multiple AI models)
- Beautiful, responsive chat interface
- Thinking indicators showing analysis process
- Spelling error suggestions with alternatives
- Educational explanations for corrections

## Prerequisites

- **Node.js** (v14 or higher) - [Download](https://nodejs.org/)
- **OpenRouter API Key** - [Get free API key](https://openrouter.ai/)

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Create `.env` File
```bash
# Copy the example file
copy .env.example .env
```

Then edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_api_key_here
PORT=3000
```

**Get your API key:**
1. Go to [openrouter.ai](https://openrouter.ai/)
2. Sign up (free account)
3. Copy your API key from the dashboard
4. Paste it in `.env`

### 3. Start the Server
```bash
npm start
```

The server will run on `http://localhost:3000`

### 4. Open in Browser
Visit: **http://localhost:3000**

## How It Works

1. **User Input**: Type your message (it can have spelling errors)
2. **Spell Check**: System detects spelling errors and suggests corrections
3. **AI Processing**: OpenRouter API analyzes your message with context
4. **Response**: Get intelligent suggestions with explanations
5. **Learning**: Understand why corrections are needed

## API Models Available

The chatbot uses **LLaMA 2 70B** by default. You can change it in `server.js`:

**Popular OpenRouter Models:**
- `meta-llama/llama-2-70b-chat` - Fast, powerful
- `openai/gpt-3.5-turbo` - Accurate
- `openai/gpt-4` - Most advanced
- `anthropic/claude-2` - Excellent for reasoning
- `mistralai/mistral-7b` - Lightweight

## Project Structure

```
autocorrect-chatbot/
├── server.js              # Express backend + OpenRouter integration
├── public/
│   └── index.html         # Frontend UI with chat interface
├── dictionary.json        # Spell checking dictionary
├── package.json           # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## API Endpoints

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
