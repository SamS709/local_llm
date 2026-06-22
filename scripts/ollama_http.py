#!/usr/bin/env python3
"""
A standalone Python script to make requests to Ollama models with system and user prompts.
"""

import requests
import json
from typing import Dict, Any, Optional

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        
        Args:
            base_url (str): The base URL of the Ollama server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
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
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if options:
            payload["options"] = options
            
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                result = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            result += data["response"]
                        if data.get("done", False):
                            break
                return {"response": result}
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
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
        print(response.get("response", "No response received"))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()