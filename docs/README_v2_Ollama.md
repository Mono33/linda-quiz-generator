# Linda Quiz Generator - Ollama Edition (v2.0)

## 🏠 Local AI Processing with Privacy

This version uses **Ollama** to run AI models locally on your machine, ensuring complete privacy and offline capability.

## 🌟 Features
- **100% Local Processing**: All AI operations run on your machine
- **Privacy First**: No data sent to external services
- **Offline Capable**: Works without internet connection
- **No Usage Costs**: Free to use once set up
- **Multiple Models**: Support for various local models

## 🚀 Setup Guide

### 1. Install Ollama
Visit [ollama.ai](https://ollama.ai/) and download Ollama for your operating system.

#### Windows
```bash
# Download and install from ollama.ai
# Or use winget
winget install Ollama.Ollama
```

#### macOS
```bash
# Download from ollama.ai or use Homebrew
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Install Python Dependencies
```bash
pip install -r requirements_ollama.txt
```

### 3. Download AI Models
```bash
# Download Mistral 7B (recommended)
ollama pull mistral

# Or try other models
ollama pull llama2
ollama pull codellama
ollama pull neural-chat
```

### 4. Start Ollama Server
```bash
ollama serve
```

### 5. Run the Application
```bash
streamlit run linda_test_eval2.py
```

## 🎯 Supported Models

| Model | Size | Best For |
|-------|------|----------|
| **mistral** | 4.1GB | General quiz generation (Recommended) |
| **llama2** | 3.8GB | Alternative general model |
| **neural-chat** | 4.1GB | Conversational responses |
| **codellama** | 3.8GB | Technical content |

## 💻 System Requirements

### Minimum
- **RAM**: 8GB
- **Storage**: 10GB free space
- **CPU**: Modern multi-core processor

### Recommended
- **RAM**: 16GB or more
- **Storage**: 20GB+ free space
- **CPU**: 8+ cores
- **GPU**: NVIDIA GPU with CUDA (optional, for faster inference)

## 🔧 Configuration

### Model Selection
In the Streamlit sidebar, you can select different models:
- Mistral 7B (Default)
- Llama 2 7B
- Neural Chat 7B
- Code Llama 7B

### Performance Tuning
```bash
# For better performance with GPU
ollama run mistral --gpu

# For CPU-only systems
ollama run mistral --cpu
```

## 🐛 Troubleshooting

### Ollama Server Not Starting
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
```

### Model Download Issues
```bash
# Check available models
ollama list

# Re-download if corrupted
ollama pull mistral --force
```

### Memory Issues
- Close other applications
- Use smaller models like `llama2:7b-chat-q4_0`
- Increase system swap space

### Connection Issues
- Ensure Ollama is running on `http://localhost:11434`
- Check firewall settings
- Verify no other service is using port 11434

## 📊 Performance Tips

1. **Use Quantized Models**: Download q4_0 or q4_1 versions for faster inference
2. **GPU Acceleration**: Enable CUDA if you have an NVIDIA GPU
3. **RAM Optimization**: Close unnecessary applications
4. **SSD Storage**: Store models on SSD for faster loading

## 🔒 Privacy Benefits

- ✅ **No Data Transmission**: All processing happens locally
- ✅ **No API Keys**: No external service registration required
- ✅ **Complete Control**: You own and control all data
- ✅ **Offline Operation**: Works without internet connection
- ✅ **No Usage Tracking**: No telemetry or usage analytics

## 🆚 vs OpenRouter Version

| Feature | Ollama (v2.0) | OpenRouter (v3.0) |
|---------|---------------|-------------------|
| **Privacy** | ✅ Complete | ⚠️ Cloud-based |
| **Setup** | ⚠️ Complex | ✅ Simple |
| **Cost** | ✅ Free | ⚠️ Pay-per-use |
| **Performance** | ⚠️ Hardware dependent | ✅ Consistent |
| **Models** | ⚠️ Limited selection | ✅ Latest models |
| **Offline** | ✅ Yes | ❌ No |

## 📞 Support

If you encounter issues:
1. Check the [Ollama Documentation](https://ollama.ai/docs)
2. Visit the [Ollama GitHub Issues](https://github.com/ollama/ollama/issues)
3. Create an issue in this repository 