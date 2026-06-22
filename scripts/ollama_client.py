#!/usr/bin/env python3
"""
A standalone Python script to make requests to Ollama models with system and user prompts.
Uses the official ollama Python library.
"""

import ollama
from typing import Dict, Any, Optional

class OllamaClient:
    """Client for interacting with Ollama API using the official Python library."""
    
    def __init__(self):
        """
        Initialize the Ollama client.
        """
        pass
    
    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response from an Ollama model.
        
        Args:
            model (str): The name of the model to use
            prompt (str): The user prompt
            system_prompt (str, optional): The system prompt
            options (dict, optional): Additional options for the generation
            stream (bool): Whether to stream the response
            
        Returns:
            dict: The response from the Ollama API
        """
        try:
            # Prepare the message structure
            messages = [{"role": "user", "content": prompt}]
            
            # Add system prompt if provided
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})
                
            # Prepare the generation parameters
            params = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            if options:
                params["options"] = options
                
            # Generate response
            response = ollama.chat(**params)
            
            return response
            
        except Exception as e:
            raise Exception(f"Error making request to Ollama: {str(e)}")

def main():
    """Example usage of the Ollama client."""
    # Create a client instance
    client = OllamaClient()
    
    # Example with system and user prompts
    try:
        response = client.generate(
            model="qwen_tuned2:latest",
            prompt="Explain quantum computing in simple terms.",
            system_prompt="You are an expert in explaining complex topics in simple terms."
        )
        
        print("Response from Ollama:")
        print(response.get("message", {}).get("content", "No response received"))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()