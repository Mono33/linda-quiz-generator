# Linda - AI Assessment Educational Platform

AI-powered educational platform for teachers and students, featuring intelligent quiz generation, student feedback, and AI-guided annotation assistance based on annotated texts.

## 🌟 Latest Version: Dual-Mode Educational Platform

This version features a **modular, scalable architecture** with **Teacher Mode** for quiz creation and **Student Mode** for AI-guided learning.

### ✨ Key Features

#### 👨‍🏫 **Teacher Mode**
- 📚 **Multi-Activity Support**: 5W, Thesis Analysis, Argumentative Essay, Connectives
- 🎯 **Intelligent Quiz Generation**: Context-aware questions based on text annotations
- 💬 **Enhanced Student Feedback**: Annotation-aware, constructive feedback with error classification
- 🌍 **Universal Language Detection**: Automatic detection for English/Italian content (all activities)
- ✏️ **Interactive Quiz Editor**: Edit, validate, and customize generated quizzes
- 📥 **Multi-Format Export**: Download quizzes as PDF, DOCX, or JSON
- 🤖 **Multiple AI Models**: Choose from Mistral, Claude, GPT-4, and more via OpenRouter

#### 👨‍🎓 **Student Mode** (NEW!)
- 📖 **AI-Guided Annotation**: Real-time hints and validation for text annotation
- 💡 **Smart Assistance**: Get contextual hints without direct answers
- ✅ **Instant Validation**: AI validates annotations and provides constructive feedback
- 🎯 **Learning Examples**: See well-crafted annotation examples when needed
- 🤔 **Metacognitive Questions**: Prompts to deepen critical thinking
- 📊 **Progress Tracking**: Export annotations to CSV for teacher review

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
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
├── linda_main_app.py           # Main application orchestrator (Teacher/Student modes)
├── core/                       # Shared components
│   ├── pdf_extractor.py        # PDF text extraction
│   ├── annotation_processor.py # CSV annotation processing
│   ├── openrouter_client.py    # OpenRouter API client
│   ├── quiz_exporter.py        # Multi-format quiz export (PDF/DOCX/JSON)
│   └── ui_components.py        # Shared UI utilities
├── activities/                 # Teacher Mode: Activity-specific modules
│   ├── activity_5w.py          # 5W quiz & feedback (fully enhanced)
│   ├── activity_thesis.py      # Thesis analysis (generic prompts)
│   ├── activity_argument.py    # Argumentative Essay (fully enhanced, Italian standards)
│   └── activity_connective.py  # Connectives analysis (generic prompts)
├── student_activities/         # Student Mode: AI-guided learning
│   └── annotation_assistant.py # AI hints, validation, examples, metacognition
└── docs/                       # Documentation & example data
    ├── example.pdf             # Example PDF for testing
    └── annotations.csv         # Example annotations
```

### Adding New Activities (Teacher Mode)

To add a new activity type:

1. Create a new file in `activities/` (e.g., `activity_newtype.py`)
2. Implement `QuizGeneratorNewType` and `FeedbackGeneratorNewType` classes
   - Follow the structure of `activity_5w.py` or `activity_argument.py` for reference
   - Include language detection logic for bilingual support
   - Define clear learning objectives in prompts
   - Add error classification in feedback prompts
3. Update the activity dropdown in `linda_main_app.py`:
   - Add mapping in `TAG_TYPE_DISPLAY_TO_INTERNAL` (if display name differs)
   - The system will automatically load your new activity

### Extending Student Mode

To enhance student assistance features:

1. Edit `student_activities/annotation_assistant.py`
2. Add new methods for additional AI guidance types
3. Update `run_student_mode()` in `linda_main_app.py` to integrate new features

---

## 📋 Supported Activity Types (Teacher Mode)

| Activity | Status | Description |
|----------|--------|-------------|
| **5W** | ✅ Fully Enhanced | Who, What, When, Where, Why analysis with language detection |
| **Argumentative Essay** | ✅ Fully Enhanced | Italian educational standards (TESI, ARGOMENTI, CONTROARGOMENTI) with error classification |
| **Thesis** | 🟡 Generic | Thesis identification and argumentation structure |
| **Connective** | 🟡 Generic | Textual connectives and cohesion analysis |

**Enhanced Activities** feature:
- ✅ Detailed educational context and learning objectives
- ✅ Sophisticated quiz generation with variation rules
- ✅ Comprehensive feedback with error classification (logical, content, interpretation, relevance, expression)
- ✅ Metacognitive questions for deeper learning
- ✅ Language-aware prompts (English/Italian)

*Generic activities have basic prompts ready. Specialized prompts can be added per activity.*

---

## 🎯 Usage Workflows

### 👨‍🏫 Teacher Mode Workflow

1. **Select Mode**: Choose "Teacher Mode" in the sidebar
2. **Upload Files**: Upload a PDF text and its corresponding CSV annotations (or use example data)
3. **Select Activity**: Choose the tag type (5W, Argumentative Essay, Thesis, Connective)
4. **Choose AI Model**: Select your preferred AI model from the dropdown
5. **Generate Quiz**: AI generates a quiz with 2 multiple-choice + 1 open-ended questions
6. **Edit Quiz** (Optional): Use the interactive quiz editor to:
   - Customize questions and answers
   - Add/delete questions
   - Validate with AI individually or all at once
   - Save changes with validation summary
7. **Test Feedback**: Load questions and test student feedback generation with sample answers
8. **Export**: Download the quiz in your preferred format (PDF, DOCX, or JSON)

### 👨‍🎓 Student Mode Workflow (NEW!)

1. **Select Mode**: Choose "Student Mode" in the sidebar
2. **Load Text**: Upload a PDF or use the example text
3. **Read & Annotate**: 
   - Read the displayed text carefully
   - Select text you want to annotate
   - Paste it into the annotation input field
   - Choose the appropriate tag type (5W, Thesis, Argument, etc.)
4. **Get AI Assistance**:
   - **Get AI Hint**: Receive contextual guidance without direct answers
   - **Validate & Save**: AI validates your annotation and provides constructive feedback
   - **See Example**: View a well-crafted annotation example when stuck
5. **Reflect**: Answer metacognitive questions to deepen your understanding
6. **Track Progress**: View your saved annotations and export them to CSV for teacher review

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

- **`core/`**: Reusable components (PDF extraction, API client, quiz export, UI helpers)
- **`activities/`**: Teacher Mode - Activity-specific quiz generation and feedback logic
- **`student_activities/`**: Student Mode - AI-guided annotation assistance
- **`linda_main_app.py`**: Main orchestrator with dual-mode support and dynamic activity loading
- **`docs/`**: Documentation, setup guides, example data
- **`backup/`**: Archived/experimental files (not in repository)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Option 1: Create .env file (recommended)
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Option 2: Export to shell
export OPENROUTER_API_KEY="your_key_here"  # Linux/Mac
$env:OPENROUTER_API_KEY="your_key_here"    # Windows PowerShell

# Run with auto-reload
streamlit run linda_main_app.py

# Run tests (if available)
pytest tests/
```

### Dependencies

```txt
streamlit>=1.28.0
PyPDF2>=3.0.0
pandas>=2.0.0
requests>=2.31.0
python-dotenv>=0.19.0
reportlab>=4.0.0
python-docx>=1.0.0
```

---

## 🌐 Deployment

### Streamlit Cloud (Recommended)

The app can be deployed to Streamlit Cloud:

1. Push your code to GitHub
2. Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud)
3. In Streamlit Cloud settings, add secrets:
   ```toml
   OPENROUTER_API_KEY = "your_key_here"
   ```
4. Select `linda_main_app.py` as the main file
5. Deploy!

**Note**: Ensure your branch name matches your Streamlit Cloud configuration (typically `main` or `master`)

### Docker

```bash
# Build the image
docker build -t linda-assessment -f docs/Dockerfile .

# Run the container
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your_key linda-assessment

# Access at http://localhost:8501
```

### Environment Variables

The app supports multiple ways to provide the API key:
1. `.env` file (local development, gitignored)
2. Environment variables (Docker, cloud platforms)
3. Streamlit secrets (Streamlit Cloud)

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

## 🎓 Educational Philosophy

**Linda** is designed with a dual approach to education:

- **Teacher Mode**: Empowers educators to create high-quality, annotation-aware assessment materials efficiently
- **Student Mode**: Provides scaffolded learning through AI-guided hints, validation, and metacognitive prompts—helping students develop critical thinking without giving away answers

The platform emphasizes:
- 📖 **Text-based learning**: Deep reading and annotation skills
- 🤔 **Critical thinking**: Metacognitive questions and reflective feedback
- 🎯 **Personalized guidance**: Context-aware AI assistance
- ✅ **Formative assessment**: Constructive feedback with error classification
- 🌍 **Multilingual support**: Seamless English/Italian content handling

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenRouter](https://openrouter.ai/)
- PDF processing via [PyPDF2](https://pypdf2.readthedocs.io/)
- Document export via [ReportLab](https://www.reportlab.com/) and [python-docx](https://python-docx.readthedocs.io/)

---

## 🆕 What's New in This Version

### v4.0 - Dual-Mode Platform (Latest)
- ✨ **Student Mode MVP**: AI-guided annotation assistance with hints, validation, examples, and metacognitive questions
- ✨ **Enhanced Argumentative Essay Activity**: Fully aligned with Italian educational standards (TESI, ARGOMENTI, CONTROARGOMENTI)
- ✨ **Multi-Format Export**: Download quizzes as PDF, DOCX, or JSON
- ✨ **Quiz Exporter Module**: Centralized export functionality
- ✨ **Universal Language Detection**: All activities now support English/Italian
- ✨ **Error Classification**: Detailed feedback with error types (logical, content, interpretation, relevance, expression)
- ✨ **Dynamic Question Generation**: Enhanced variation rules to prevent repetitive questions
- ✨ **Improved UX**: Validation summaries, persistent model selection, better quiz editor workflows

### Previous Versions
- **v3.0** (Monolithic): Available in `backup/` folder (local only)
- **v2.0** (Ollama): See [docs/README_OLLAMA.md](docs/README_OLLAMA.md)

---

## 📧 Contact & Support

- **Issues & Bug Reports**: [Open an issue on GitHub](https://github.com/Mono33/linda-quiz-generator/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Mono33/linda-quiz-generator/discussions)
- **Organization Repository**: [FEM-modena/linda_ai_tools](https://github.com/FEM-modena/linda_ai_tools)

---

## 🔮 Roadmap

- [ ] **Student Mode Phase 2**: Progress dashboard, annotation history, performance analytics
- [ ] **More Activities**: Enhance Thesis and Connective activities with specialized prompts
- [ ] **Batch Processing**: Generate quizzes for multiple texts at once
- [ ] **Custom Prompt Templates**: Allow teachers to define their own prompt templates
- [ ] **Collaboration Features**: Share quizzes and annotations between teachers
- [ ] **Mobile Optimization**: Improved mobile UI for student annotation on tablets
