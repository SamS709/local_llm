# Ollama Client

A simple Python client for interacting with Ollama models using the official Python library.

## Installation

Before using this client, you need to install the ollama Python package:

```bash
pip install ollama
```

## Usage

```python
from ollama_client import OllamaClient

client = OllamaClient()

# Basic usage
response = client.generate(
    model="llama3",
    prompt="Explain quantum computing in simple terms."
)

print(response.get("message", {}).get("content"))

# With system prompt
response = client.generate(
    model="llama3",
    prompt="What are the benefits of renewable energy?",
    system_prompt="You are an expert in environmental science and sustainability."
)

print(response.get("message", {}).get("content"))
```

## Features

- Support for system prompts and user prompts
- Streaming responses
- Error handling
- Compatible with all Ollama models

## Requirements

- Python 3.6+
- Ollama installed and running locally
- An Ollama model (e.g., llama3) downloaded