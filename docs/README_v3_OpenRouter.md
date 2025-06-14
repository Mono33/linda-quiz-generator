# Linda Quiz Generator - OpenRouter Edition (v3.0) ⭐

## ☁️ Cloud-Powered AI with Cutting-Edge Models

This version uses **OpenRouter** to access the latest AI models in the cloud, providing easy setup and powerful performance.

## 🌟 Features
- **Easy Setup**: No local AI installation required
- **Latest Models**: Access to GPT, Claude, Mistral, and more
- **Consistent Performance**: Cloud-based processing
- **Automatic Updates**: Always use the newest model versions
- **Scalable**: No hardware limitations

## 🚀 Quick Setup (5 minutes)

### 1. Get OpenRouter API Key
1. Visit [openrouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Go to "Keys" section
4. Generate a new API key
5. Copy your API key (starts with `sk-or-v1-...`)

### 2. Install Dependencies
```bash
pip install -r requirements_openrouter.txt
```

### 3. Set Your API Key

#### Option A: Environment Variable (Recommended)
```bash
# Windows PowerShell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key-here"

# Windows Command Prompt
set OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Linux/macOS
export OPENROUTER_API_KEY="sk-or-v1-your-key-here"
```

#### Option B: .env File
Create a `.env` file in the project directory:
```bash
echo "OPENROUTER_API_KEY=sk-or-v1-your-key-here" > .env
```

### 4. Run the Application
```bash
streamlit run linda_test_eval3.py
```

## 🎯 Available Models

| Model | Provider | Best For | Cost/1M tokens |
|-------|----------|----------|----------------|
| **Mistral 7B** ⭐ | Mistral | General use (Recommended) | $0.20 |
| **GPT-3.5 Turbo** | OpenAI | Fast responses | $0.50 |
| **Claude 3 Haiku** | Anthropic | Balanced performance | $0.25 |
| **Llama 2 7B** | Meta | Open source alternative | $0.20 |
| **Gemma 7B** | Google | Efficient processing | $0.20 |

## 💰 Pricing

OpenRouter uses **pay-per-use** pricing:

### Typical Usage Costs
- **Quiz Generation**: $0.01-0.05 per quiz
- **Question Validation**: $0.001-0.01 per question
- **Feedback Generation**: $0.005-0.02 per feedback

### Monthly Estimates
- **Light Use** (10 quizzes/month): ~$0.50
- **Regular Use** (50 quizzes/month): ~$2.50
- **Heavy Use** (200 quizzes/month): ~$10.00

### Free Credits
- New accounts get **$5 free credits**
- Enough for ~100-500 quizzes depending on model

## 🔧 Configuration

### Model Selection
In the Streamlit sidebar, choose from:
- **Mistral 7B** (Recommended for most users)
- **GPT-3.5 Turbo** (Fast and reliable)
- **Claude 3 Haiku** (Great reasoning)
- **Llama 2 7B** (Open source)

### Advanced Settings
```python
# In the app, you can adjust:
- Temperature (creativity level)
- Max tokens (response length)
- Model selection per task
```

## 🐛 Troubleshooting

### API Key Issues
```bash
# Check if key is set
echo $OPENROUTER_API_KEY

# Test API connection
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models
```

### Common Error Messages

#### "OpenRouter API key not found"
- Set the `OPENROUTER_API_KEY` environment variable
- Check the `.env` file exists and has correct format

#### "API key is invalid"
- Verify your API key on openrouter.ai
- Ensure key starts with `sk-or-v1-`

#### "Insufficient credits"
- Check your balance on openrouter.ai
- Add credits to your account

#### "Rate limit exceeded"
- Wait a few seconds and try again
- Consider upgrading your plan for higher limits

## 📊 Performance Optimization

### Model Selection Tips
1. **For Speed**: Use Mistral 7B or GPT-3.5 Turbo
2. **For Quality**: Use Claude 3 Haiku or GPT-4
3. **For Cost**: Use Llama 2 7B or Gemma 7B
4. **For Balance**: Use Mistral 7B (recommended)

### Cost Optimization
```python
# Reduce costs by:
- Using shorter prompts
- Lowering max_tokens setting
- Choosing cheaper models for simple tasks
- Batching multiple questions
```

## 🔒 Security & Privacy

### Data Handling
- ⚠️ **Data sent to cloud**: Text and annotations are processed by OpenRouter
- ✅ **No data storage**: OpenRouter doesn't store your data permanently
- ✅ **Encrypted transmission**: All data sent via HTTPS
- ✅ **API key security**: Keys are encrypted in transit

### Best Practices
```bash
# Keep API keys secure
- Never commit keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor usage on OpenRouter dashboard
```

## 🆚 vs Ollama Version

| Feature | OpenRouter (v3.0) | Ollama (v2.0) |
|---------|-------------------|---------------|
| **Setup Time** | ✅ 5 minutes | ⚠️ 30+ minutes |
| **Hardware Needs** | ✅ Any computer | ⚠️ 8GB+ RAM |
| **Model Access** | ✅ Latest models | ⚠️ Limited selection |
| **Performance** | ✅ Consistent | ⚠️ Hardware dependent |
| **Privacy** | ⚠️ Cloud-based | ✅ 100% local |
| **Cost** | ⚠️ Pay-per-use | ✅ Free after setup |
| **Internet** | ❌ Required | ✅ Offline capable |

## 🌐 Deployment Options

### Streamlit Cloud
```bash
# Deploy to Streamlit Cloud
1. Push code to GitHub
2. Connect to streamlit.io
3. Add OPENROUTER_API_KEY to secrets
4. Deploy!
```

### Heroku
```bash
# Set environment variable
heroku config:set OPENROUTER_API_KEY=your-key-here
```

### Docker
```dockerfile
ENV OPENROUTER_API_KEY=your-key-here
```

## 📞 Support

### OpenRouter Support
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Discord](https://discord.gg/openrouter)
- Email: support@openrouter.ai

### This Project
- Create an issue in this GitHub repository
- Check existing issues for solutions
- Contribute improvements via pull requests

## 🎯 Getting Started Checklist

- [ ] Sign up at openrouter.ai
- [ ] Generate API key
- [ ] Install requirements: `pip install -r requirements_openrouter.txt`
- [ ] Set environment variable: `export OPENROUTER_API_KEY="your-key"`
- [ ] Run app: `streamlit run linda_test_eval3.py`
- [ ] Upload PDF and annotations
- [ ] Generate your first quiz!

**Ready to start? This version is recommended for most users!** 🚀 