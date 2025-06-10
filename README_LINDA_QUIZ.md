# Linda Quiz Generator - AI-Powered Educational Assessment Tool

An intelligent quiz generation system that creates comprehension assessments from annotated texts using local AI models via Ollama.

## 🎯 Overview

Linda Quiz Generator helps educators create personalized comprehension quizzes based on annotated texts. The system provides:

1. **PDF Text Extraction** - Extract content from PDF documents
2. **Annotation Processing** - Process CSV annotation data (5W tags, Thesis, Arguments, Connectives)
3. **AI Quiz Generation** - Create multiple-choice and open-ended questions using local AI models
4. **Interactive Quiz Editor** - Edit and validate generated questions with AI assistance
5. **Student Feedback System** - Provide automated feedback on student responses

## ✨ Key Features

### 🤖 **Local AI Processing**
- Uses Ollama for privacy-focused, local AI processing
- No data sent to external services
- Multiple model support (Mistral, Gemma, Phi-3, etc.)

### 📝 **Dynamic Quiz Generation**
- Adapts questions based on annotation types (5W, Thesis, Argument, Connective)
- Creates contextually relevant multiple-choice and open-ended questions
- Fallback system when AI is unavailable

### ✏️ **Interactive Editor**
- Edit generated questions in real-time
- AI-powered validation of question accuracy
- Add, remove, or modify questions easily

### 🎨 **Modern Interface**
- Clean, intuitive Streamlit web interface
- Real-time status updates
- Dynamic model selection

## 🔧 Requirements

- **Python**: 3.9 or higher
- **Ollama**: [Download and install](https://ollama.ai/download)
- **System**: Compatible with Windows, macOS, Linux

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd linda_eval
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e .
```
*This installs the project and all dependencies from `pyproject.toml`*

### 4. Install and Configure Ollama

1. Download Ollama from [ollama.ai/download](https://ollama.ai/download)
2. Install following the platform-specific instructions
3. Pull your preferred model:
```bash
# Recommended models:
ollama pull mistral        # General purpose, good balance
ollama pull gemma3:1b     # Lightweight, fast
ollama pull phi3:mini     # Microsoft's efficient model
```

### 5. Start Ollama Server
```bash
ollama serve
```

## 🎮 Usage

### 1. Launch the Application
```bash
streamlit run linda_test_eval2.py
```

### 2. Configure Settings
- **Tag Type**: Select annotation type (5W, Thesis, Argument, Connective)
- **AI Model**: Choose from available Ollama models
- **Update Model**: Apply model changes (or it updates automatically during generation)

### 3. Upload Content
- **PDF File**: Upload the text document
- **Annotations CSV**: Upload the corresponding annotations
- **Example Data**: Use built-in sample data for testing

### 4. Generate and Edit Quiz
- Click **"Generate Quiz"** to create questions
- Use **"Edit Quiz"** to modify questions interactively
- **AI Validation**: Validate questions against the source text
- **Download**: Export quiz as JSON

### 5. Test Student Responses
- Enter student answers in the feedback section
- Get AI-powered feedback and suggestions

## 📊 Supported Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `mistral` | ~4GB | Medium | High | General use, balanced performance |
| `gemma3:1b` | ~1GB | Fast | Good | Quick generation, limited resources |
| `phi3:mini` | ~2GB | Fast | Good | Efficient, Microsoft-optimized |
| `gemma3:4b` | ~4GB | Medium | High | Better quality, more resources |

## 📁 File Formats

### PDF Documents
- Any PDF with extractable text
- Educational articles, stories, essays
- Multi-page documents supported

### Annotations CSV
Required columns:
```csv
code,title,begin,end,text
WHO,WHO,7,15,Samardo Samuels
WHEN,WHEN,0,9,Mercoledì
WHERE,WHERE,45,65,condominio di Milano
WHAT,WHAT,20,35,comportamento intimidatorio
WHY,WHY,100,120,violazione del divieto
```

## 🎯 Quiz Types

### 5W Questions
Focus on: **Who, What, When, Where, Why**
- Ideal for narrative texts and news articles
- Tests factual comprehension

### Thesis Questions  
Focus on: **Main arguments and supporting evidence**
- Perfect for argumentative texts
- Analyzes logical structure

### Argument Questions
Focus on: **Logical reasoning and premises**
- Evaluates critical thinking
- Identifies argumentative patterns

### Connective Questions
Focus on: **Text cohesion and linguistic markers**
- Examines discourse structure
- Tests understanding of text flow

## 🔧 Advanced Features

### AI Question Validation
- Automatically checks if answers align with source text
- Provides suggestions for improvement
- Explains reasoning behind validation

### Fallback System
- Works even when Ollama is unavailable
- Uses template-based question generation
- Ensures continuous functionality

### Session Persistence
- Maintains state across page refreshes
- Preserves uploaded files and generated content
- Seamless user experience

## 🛠️ Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
ollama serve

# Pull missing models
ollama pull mistral
```

### Common Problems
- **"Model not found"**: Pull the model with `ollama pull <model-name>`
- **"Connection refused"**: Ensure Ollama server is running
- **Slow generation**: Try a smaller model like `gemma3:1b`
- **Memory issues**: Use quantized models or increase system RAM

### Performance Tips
- Use `gemma3:1b` for faster generation
- Close other applications to free memory
- Consider SSD storage for better model loading

## 🔒 Privacy & Security

- **Local Processing**: All AI processing happens on your machine
- **No External Calls**: No data sent to cloud services
- **Secure**: Your educational content stays private
- **GDPR Compliant**: No personal data collection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Ollama documentation
3. Open an issue on GitHub

---

**Made with ❤️ for educators who want to create better assessments with AI** 