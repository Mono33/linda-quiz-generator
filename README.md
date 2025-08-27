# Linda Quiz Generator

AI-powered quiz generation tool for educational content based on annotated texts.

## 🚀 Available Versions

### Version 2.0 - Ollama Edition (`linda_test_eval2.py`)
- **Backend**: Local Ollama server
- **Pros**: Privacy, offline capability, no API costs
- **Cons**: Requires local setup, limited to local models
- **Setup**: [Ollama Setup Guide](docs/README_v2_Ollama.md)

### Version 3.0 - OpenRouter Edition (`linda_test_eval3.py`) ⭐ **Recommended**
- **Backend**: OpenRouter cloud API
- **Pros**: Easy setup, access to latest models, no local resources needed
- **Cons**: Requires API key, internet connection, usage costs
- **Setup**: [OpenRouter Setup Guide](docs/README_v3_OpenRouter.md)

## 🎯 Which Version Should I Use?

| Use Case | Recommended Version |
|----------|-------------------|
| **Quick start, cloud-based** | Version 3.0 (OpenRouter) |
| **Privacy-focused, offline** | Version 2.0 (Ollama) |
| **Educational institutions** | Version 3.0 (OpenRouter) |
| **Personal/research use** | Version 2.0 (Ollama) |

## 🛠️ Quick Start

### OpenRouter Version (Recommended)
## app deployata: https://share.streamlit.io/app/mono33-linda-quiz-generator-linda-test-eval3/
```bash
pip install -r requirements_openrouter.txt
export OPENROUTER_API_KEY="your_key_here"
streamlit run linda_test_eval3.py
```

### Ollama Version
```bash
pip install -r requirements_ollama.txt
# Install and start Ollama server first
streamlit run linda_test_eval2.py
```

## 📚 Features
- Upload PDF texts and CSV annotations
- Generate comprehension quizzes using AI
- Support for multiple annotation types (5W, Thesis, Argument, Connective)
- Interactive quiz editor with validation
- Export quizzes as JSON

## 🎥 Demo
Check out the demo video: `demo_ai_assessment.mp4`

## 🔧 Development
Both versions share the same core functionality but use different AI backends:
- **v2.0**: Uses local Ollama models for privacy and offline use
- **v3.0**: Uses OpenRouter API for easy access to cutting-edge models

## 📄 License
This project is open source and available under the MIT License.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 