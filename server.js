const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;

app.use(express.json());
app.use(cors());
app.use(express.static('public'));

// Spell checking dictionary (basic)
const dictionary = new Set(require('./dictionary.json'));

// Check spelling
function checkSpelling(text) {
  const words = text.toLowerCase().split(/\s+/);
  const errors = [];
  
  words.forEach((word, index) => {
    const cleanWord = word.replace(/[.,!?;:]/g, '');
    if (cleanWord && !dictionary.has(cleanWord)) {
      errors.push({
        word: cleanWord,
        position: index,
        suggestions: getSuggestions(cleanWord)
      });
    }
  });
  
  return errors;
}

// Get spell correction suggestions using edit distance
function getSuggestions(word, maxDistance = 2) {
  const suggestions = [];
  const dictArray = Array.from(dictionary);
  
  dictArray.forEach(dictWord => {
    const distance = levenshteinDistance(word, dictWord);
    if (distance <= maxDistance && distance > 0) {
      suggestions.push({
        word: dictWord,
        distance: distance
      });
    }
  });
  
  return suggestions
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 5)
    .map(s => s.word);
}

// Levenshtein distance algorithm
function levenshteinDistance(a, b) {
  const matrix = [];
  
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }
  
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  
  return matrix[b.length][a.length];
}

// Chat endpoint with OpenRouter API
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message || !message.trim()) {
      return res.status(400).json({ error: 'Message is required' });
    }
    
    // Check spelling
    const spellingErrors = checkSpelling(message);
    
    // Build system prompt for the AI
    const systemPrompt = `You are a helpful spell-checking and grammar assistant chatbot named "Think". 
Your role is to:
1. Check for spelling and grammar errors in user messages
2. Provide corrections with explanations
3. Help improve writing quality
4. Have thoughtful conversations about language and writing

When responding:
- Be friendly and educational
- Explain why corrections are needed
- Provide examples when helpful
- Use clear, concise language`;

    // Build user message with spelling context
    let userMessage = message;
    if (spellingErrors.length > 0) {
      userMessage += `\n\n[System: Potential spelling errors detected: ${spellingErrors.map(e => `"${e.word}" (suggestions: ${e.suggestions.join(', ')})`).join('; ')}]`;
    }
    
    // Call OpenRouter API with streaming
    const response = await axios.post(
      'https://openrouter.ai/api/v1/chat/completions',
      {
        model: 'meta-llama/llama-2-70b-chat',
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userMessage
          }
        ],
        temperature: 0.7,
        max_tokens: 1000,
        top_p: 0.9
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
          'HTTP-Referer': 'http://localhost:3000',
          'X-Title': 'Autocorrect Chatbot'
        }
      }
    );
    
    const aiResponse = response.data.choices[0].message.content;
    
    res.json({
      message: aiResponse,
      spellingErrors: spellingErrors,
      thinking: spellingErrors.length > 0 ? `Found ${spellingErrors.length} potential spelling error(s). Analyzing...` : 'Processing your message...'
    });
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Failed to process request',
      details: error.response?.data?.error?.message || error.message
    });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running' });
});

app.listen(PORT, () => {
  console.log(`✓ Spell-Check Chatbot running on http://localhost:${PORT}`);
  console.log(`✓ Open http://localhost:${PORT} in your browser`);
});
