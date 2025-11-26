# 🔐 Linda Test Eval 3.0 - Setup Guide

## API Key Configuration Options

### 🥇 Option 1: Environment Variables (RECOMMENDED)

This is the **most secure** method and works across all environments.

#### Windows PowerShell:
```powershell
# Temporary (current session only)
$env:OPENROUTER_API_KEY="sk-or-your-actual-key-here"

# Permanent (user-level)
[System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-your-actual-key-here", "User")

# Verify it's set
echo $env:OPENROUTER_API_KEY
```

#### Windows Command Prompt:
```cmd
# Temporary (current session only)
set OPENROUTER_API_KEY=sk-or-your-actual-key-here

# Verify it's set
echo %OPENROUTER_API_KEY%
```

#### Linux/Mac:
```bash
# Temporary (current session only)
export OPENROUTER_API_KEY="sk-or-your-actual-key-here"

# Permanent (add to ~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export OPENROUTER_API_KEY="sk-or-your-actual-key-here"' >> ~/.bashrc
source ~/.bashrc

# Verify it's set
echo $OPENROUTER_API_KEY
```

### 🥈 Option 2: .env File (GOOD)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```
   OPENROUTER_API_KEY=sk-or-your-actual-key-here
   ```

3. The `.env` file is automatically loaded by the application
4. **Important**: Never commit `.env` to version control (it's in `.gitignore`)

### 🥉 Option 3: Streamlit Secrets (FOR DEPLOYMENT)

For Streamlit Cloud deployment:

1. Create `.streamlit/secrets.toml`:
   ```toml
   OPENROUTER_API_KEY = "sk-or-your-actual-key-here"
   ```

2. Add to `.gitignore`:
   ```
   .streamlit/secrets.toml
   ```

### ⚠️ Option 4: Sidebar Input (DEVELOPMENT ONLY)

- Use only for testing/development
- Not recommended for production
- The app will warn you about security

## 🚀 Getting Your OpenRouter API Key

1. **Visit**: https://openrouter.ai/
2. **Sign up** for a free account
3. **Navigate** to "Keys" in your dashboard
4. **Create** a new API key
5. **Copy** the key (starts with `sk-or-`)
6. **Configure** using one of the methods above

## 💰 Cost Information

OpenRouter is very affordable:

| Model | Cost per 1K tokens | Typical Quiz Cost |
|-------|-------------------|-------------------|
| Mistral 7B | €0.0001 | €0.01-0.02 |
| Claude 3 Haiku | €0.00025 | €0.02-0.05 |
| GPT-3.5 Turbo | €0.0005 | €0.03-0.08 |

**Much cheaper than buying new hardware!**

## 🔒 Security Best Practices

### ✅ DO:
- Use environment variables
- Use `.env` files (not committed)
- Use Streamlit secrets for deployment
- Rotate keys regularly
- Use different keys for different projects

### ❌ DON'T:
- Hardcode keys in source code
- Commit keys to version control
- Share keys in chat/email
- Use the same key everywhere
- Leave keys in public repositories

## 🛠️ Installation & Running

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key** (choose one method above)

3. **Run the application**:
   ```bash
   streamlit run linda_test_eval3.py
   ```

## 🔧 Troubleshooting

### "API Key not found"
- Check environment variable is set correctly
- Restart terminal/IDE after setting environment variables
- Verify `.env` file is in the correct directory

### "API request failed"
- Check your API key is valid
- Verify you have credits in your OpenRouter account
- Check internet connection

### "Model not available"
- Some models may have usage limits
- Try a different model from the dropdown
- Check OpenRouter status page

## 🤝 For Your Colleagues

When sharing this project:

1. **Share the code** (without any API keys)
2. **Share this setup guide**
3. **Each person needs their own API key**
4. **Recommend environment variables** for security

### Quick Start for Colleagues:
```bash
# 1. Clone the repository
git clone https://github.com/Mono33/linda-quiz-generator.git
cd linda-quiz-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get API key from https://openrouter.ai/

# 4. Set environment variable (Windows PowerShell)
$env:OPENROUTER_API_KEY="your-key-here"

# 5. Run the app
streamlit run linda_test_eval3.py
```

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify your API key setup
3. Check OpenRouter documentation
4. Create an issue in the repository

---

**Remember**: Keep your API keys secure and never share them publicly! 