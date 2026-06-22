from litellm import completion
import os


message = """



"""

# Using Ollama with lite_llm
import asyncio
from litellm import acompletion
from dotenv import load_dotenv

load_dotenv()

async def main():
    response = await acompletion(
        model="ollama/qwen_tuned2:latest",  # Format for Ollama models
    messages=[
        {"role": "user", "content": "Explique la différence entre Docker et une VM en 3 lignes."}
    ],
    api_base="http://localhost:11434",  # Ollama default address
    )
    print(response.choices[0].message.content)
    print(response.usage.total_tokens)

asyncio.run(main())
print("coucou")
