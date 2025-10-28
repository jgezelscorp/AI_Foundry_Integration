# Multi-Agent System: Foundry + Yoda

A Python console application demonstrating an **agentic pattern** with:
- **Foundry Search Agent**: Connects to Azure AI Foundry for web search
- **Yoda Transform Agent**: Uses Semantic Kernel to transform responses into Yoda speak
- **Orchestrator**: Coordinates the workflow between agents

## Prerequisites

- Python 3.8 or higher
- Azure CLI installed and authenticated (`az login`)
- Access to Azure AI Foundry project

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment:**
   - Copy `.env.example` to `.env` (already done)
   - Update `.env` with your Azure AI Foundry and OpenAI details:
     ```
     PROJECT_ENDPOINT=https://jgeazureaiservice.services.ai.azure.com/api/projects/jgeazureaiservice-project
     AGENT_ID=asst_rp449pIu5jSjpXXWJp8Up6Ke
     AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
     AZURE_OPENAI_DEPLOYMENT=gpt-4o
     ```

## Usage

### Interactive Mode

Run the application without arguments to enter interactive chat mode:

```bash
python agent_console.py
```

Then type your queries and press Enter. Commands:
- Type any query to search and transform into Yoda speak
- `yoda off` - Disable Yoda transformation
- `yoda on` - Enable Yoda transformation  
- `exit`, `quit` - End session

### Single Query Mode

Send a single query with Yoda transformation:

```bash
python agent_console.py "What is Azure AI Foundry?"
```

Send a single query WITHOUT Yoda transformation:

```bash
python agent_console.py "What is Azure AI Foundry?" --no-yoda
```

### Examples

```bash
# Interactive mode with Yoda transformation
python agent_console.py

# Single query with Yoda
python agent_console.py "Explain what AI agents are"

# Single query without Yoda
python agent_console.py "Tell me about Microsoft Build 2024" --no-yoda
```

## Features

- ✅ **Multi-Agent Architecture**: Orchestrated workflow between two specialized agents
- ✅ **Foundry Search Agent**: Leverages Azure AI Foundry for web search and information retrieval
- ✅ **Yoda Transform Agent**: Uses Semantic Kernel + Azure OpenAI to transform responses into Yoda speak
- ✅ **Agentic Pattern**: Demonstrates agent orchestration and coordination
- ✅ **Interactive chat mode**: Continuous conversation with toggle for Yoda transformation
- ✅ **Single query mode**: Command-line execution with optional `--no-yoda` flag
- ✅ **Automatic thread management**: Creates and cleans up conversation threads
- ✅ **Real-time progress indicators**: Visual feedback for each agent's operation
- ✅ **Error handling**: Detailed error messages with stack traces

## Authentication

The application uses `DefaultAzureCredential` which supports multiple authentication methods in this order:

1. **Environment variables** (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
2. **Managed Identity** (when running in Azure)
3. **Azure CLI** (if you've run `az login`)
4. **Visual Studio Code** (if signed in)
5. **Azure PowerShell** (if authenticated)

For local development, the easiest method is:
```bash
az login
```

## Project Structure

```
python-agent/
├── agent_console.py      # Main application
├── requirements.txt      # Python dependencies
├── .env                  # Configuration (your settings)
├── .env.example         # Configuration template
└── README.md            # This file
```

## Troubleshooting

### Authentication Error
If you get authentication errors:
```bash
az login
az account show  # Verify you're logged in
```

### Module Not Found
Make sure you've activated the virtual environment and installed dependencies:
```bash
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### Agent Not Found
Verify your `AGENT_ID` in `.env` matches the agent ID in Azure AI Foundry.

### Connection Error
Verify your `PROJECT_ENDPOINT` in `.env` is correct and you have access to the Azure AI Foundry project.

## API Reference

The application uses the Azure AI Projects SDK:
- [Azure AI Projects SDK Documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
