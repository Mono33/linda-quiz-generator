# Linda - AI Assessment Educational Platform

AI-powered quiz generation and student feedback tool for educational content based on annotated texts.

## 🌟 Latest Version: Modular Architecture with OpenRouter

This version features a **modular, scalable architecture** that supports multiple activity types with specialized quiz generation and intelligent student feedback.

### ✨ Key Features

- 📚 **Multi-Activity Support**: 5W, Thesis Analysis, Argumentative Text, Connectives
- 🎯 **Intelligent Quiz Generation**: Context-aware questions based on text annotations
- 💬 **Enhanced Student Feedback**: Annotation-aware, constructive feedback for both open-ended and multiple-choice questions
- 🌍 **Language Detection**: Automatic detection for English/Italian content (5W activity)
- ✏️ **Interactive Quiz Editor**: Edit, validate, and customize generated quizzes
- 🤖 **Multiple AI Models**: Choose from Mistral, Claude, GPT-4, and more via OpenRouter

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key ([Get one here](https://openrouter.ai/))

### Installation

```bash
# Clone the repository
git clone https://github.com/Mono33/linda-quiz-generator.git
cd linda-quiz-generator

# Install dependencies
pip install -r requirements.txt

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your_key_here"  # Linux/Mac
$env:OPENROUTER_API_KEY="your_key_here"    # Windows PowerShell
```

### Run the Application

```bash
streamlit run linda_main_app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 🏗️ Architecture

### Modular Design

The application follows a clean, modular architecture for easy maintenance and extensibility:

```
linda_eval/
├── linda_main_app.py           # Main application orchestrator
├── core/                       # Shared components
│   ├── pdf_extractor.py        # PDF text extraction
│   ├── annotation_processor.py # CSV annotation processing
│   ├── openrouter_client.py   # OpenRouter API client
│   └── ui_components.py        # Shared UI utilities
├── activities/                 # Activity-specific modules
│   ├── activity_5w.py          # 5W quiz & feedback (enhanced)
│   ├── activity_thesis.py      # Thesis analysis
│   ├── activity_argument.py    # Argumentative text
│   └── activity_connective.py  # Connectives analysis
└── docs/                       # Documentation & extras
```

### Adding New Activities

To add a new activity type:

1. Create a new file in `activities/` (e.g., `activity_newtype.py`)
2. Implement `QuizGeneratorNewType` and `FeedbackGeneratorNewType` classes
3. Register the activity in `linda_main_app.py` in the `ACTIVITY_REGISTRY`

---

## 📋 Supported Activity Types

| Activity | Status | Description |
|----------|--------|-------------|
| **5W** | ✅ Enhanced | Who, What, When, Where, Why analysis with language detection |
| **Thesis** | 🟡 Generic | Thesis identification and argumentation structure |
| **Argument** | 🟡 Generic | Argumentative reasoning and logic analysis |
| **Connective** | 🟡 Generic | Textual connectives and cohesion analysis |

*Generic activities have basic prompts ready. Specialized prompts can be added per activity.*

---

## 🎯 Usage Workflow

1. **Upload Files**: Upload a PDF text and its corresponding CSV annotations
2. **Select Activity**: Choose the tag type (5W, Thesis, Argument, Connective)
3. **Generate Quiz**: AI generates a quiz with 2 multiple-choice + 1 open-ended questions
4. **Edit Quiz** (Optional): Use the interactive editor to customize questions
5. **Test Feedback**: Load questions and test student feedback generation
6. **Export**: Download the quiz as JSON

---

## 🤖 Available AI Models

Via OpenRouter, you can choose from:

- **Mistral 7B** (Fast, cost-effective)
- **Claude 3.5 Haiku** (Balanced performance)
- **Claude 3.5 Sonnet** (Advanced reasoning)
- **GPT-3.5 Turbo** (Fast, general purpose)
- **GPT-4o** (Advanced capabilities)
- **GPT-4o Mini** (Efficient, cost-effective)
- **Gemma 3 4B** (Free tier available)

Select your preferred model in the sidebar.

---

## 📚 Documentation

- **Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **Ollama Version**: [docs/README_OLLAMA.md](docs/README_OLLAMA.md) *(historical)*
- **Demo Video**: [docs/demo_ai_assessment.mp4](docs/demo_ai_assessment.mp4)
- **Docker Setup**: [docs/Dockerfile](docs/Dockerfile)

---

## 🎥 Demo

Watch the application in action: [docs/demo_ai_assessment.mp4](docs/demo_ai_assessment.mp4)

---

## 🔧 Development

### Project Structure

- **`core/`**: Reusable components (PDF extraction, API client, UI helpers)
- **`activities/`**: Activity-specific quiz generation and feedback logic
- **`linda_main_app.py`**: Main orchestrator with dynamic activity loading

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run linda_main_app.py

# Run tests (if available)
pytest tests/
```

---

## 🌐 Deployment

### Streamlit Cloud

The app can be deployed to Streamlit Cloud:

1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `OPENROUTER_API_KEY` to secrets
4. Deploy!

### Docker

```bash
docker build -t linda-assessment -f docs/Dockerfile .
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your_key linda-assessment
```

---

## 🔒 Privacy & Security

- **API Keys**: Never commit API keys. Use environment variables or `.env` files (gitignored)
- **Data Privacy**: Uploaded files are processed in memory and not permanently stored
- **OpenRouter**: Data handling follows [OpenRouter's privacy policy](https://openrouter.ai/privacy)

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenRouter](https://openrouter.ai/)
- PDF processing via [PyPDF2](https://pypdf2.readthedocs.io/)

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Previous Versions:**
- Version 2.0 (Ollama): See [docs/README_OLLAMA.md](docs/README_OLLAMA.md)
- Version 3.0 (Monolithic): Available in `backup/` folder (local only)
