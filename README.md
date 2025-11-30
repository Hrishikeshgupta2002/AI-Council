# Agentic Council System

A beautiful CLI-based multi-agent council system that uses 4 specialized Ollama agents to analyze problems through parallel responses, natural group chat discussions, and weighted synthesis.

![Agentic Council System Demo](Untitled%20design.gif)

## 🎯 Features

- 🎨 **Beautiful CLI** with rich formatting and colors
- 💬 **Natural group chat** conversations between agents
- 🏷️ **Tag agents** with @mentions for focused debates
- ⚖️ **Weighted decision model** for final recommendations
- 🔍 **Comprehensive synthesis** analysis
- 🚀 **Parallel agent processing** for speed
- 📊 **Structured output** with agreements, conflicts, and blind spots

## 🏗️ Architecture

The system consists of 4 specialized agents, each with a distinct persona and thinking layer:

1. **Elon** (Visionary) - First-principles thinking, innovation, bold direction
2. **Sam** (Strategist) - Business model, market realities, scalability
3. **Sheryl** (Operator) - Practical execution, system design, reliability
4. **Ray** (Risk Analyst) - Red-team, failure modes, blind spots

## 📦 Installation

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running:
   ```bash
   ollama serve
   ```

3. **Pull required models:**
   ```bash
   ollama pull gpt-oss:120b-cloud
   ollama pull glm-4.6:cloud
   ollama pull kimi-k2-thinking:cloud
   ollama pull deepseek-v3.1:671b-cloud
   ```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-council.git
cd agentic-council

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

## 🚀 Usage

### Basic Usage

```bash
python main.py
```

Enter your problem statement when prompted, and the council will analyze it.

### Command Line Arguments

```bash
# Direct input
python main.py "Your problem statement here"

# Piped input
echo "Your problem statement" | python main.py
```

### Interactive Features

- **Normal message**: Type your message, all agents respond
- **Tag agents**: Use `@Elon @Sam debate this topic` to start a focused debate
- **Continue conversation**: Press Enter to continue the general conversation
- **Exit**: Type `exit`, `quit`, or `q` to end

### Example

```bash
$ python main.py
Enter your problem statement: Should we build this feature?

# Agents respond...

> @Elon @Sam debate the technical approach
# Tagged agents have a focused 2-3 exchange debate

> # Press Enter for another round
# Agents can choose to respond or skip
```

## ⚙️ Configuration

Set environment variables to customize behavior:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"  # Ollama server URL
export USE_WEIGHTED_MODEL="true"                  # Use weighted model (default: true)
export AGENT_TIMEOUT="60"                         # Agent response timeout in seconds
export MAX_WORKERS="4"                            # Max parallel workers
export DEBUG="true"                                # Show detailed error traces
```

## 📁 Project Structure

```
agentic-council/
├── agents/              # Agent implementations
│   ├── __init__.py
│   ├── visionary.py
│   ├── strategist.py
│   ├── operator.py
│   └── risk_analyst.py
├── council.py           # Council orchestrator
├── synthesis.py         # Synthesis agent
├── state.py             # State management
├── config.py            # Configuration module
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup
├── pyproject.toml      # Modern Python packaging
├── LICENSE             # MIT License
└── README.md           # This file
```

## 🧩 Module Overview

- **`council.py`**: Main orchestrator managing agent interactions
- **`agents/`**: Individual agent implementations with distinct personas
- **`synthesis.py`**: Meta-agent that synthesizes all responses
- **`state.py`**: State management for conversation tracking
- **`config.py`**: Centralized configuration management
- **`main.py`**: CLI interface with rich formatting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [Ollama](https://ollama.ai/)
- Beautiful CLI with [Rich](https://github.com/Textualize/rich)
