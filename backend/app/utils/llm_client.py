import json
import re
import random
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config
from .logger import get_logger

logger = get_logger('mirofish.llm_client')


class LLMClient:
    """Lightweight LLM client supporting multiple providers."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        # Allow explicit override for a single client
        if api_key or base_url or model:
            self.api_key = api_key or Config.LLM_API_KEY
            self.base_url = base_url or Config.LLM_BASE_URL
            self.model = model or Config.LLM_MODEL_NAME
            
            if not self.api_key:
                raise ValueError("LLM_API_KEY is not configured")
            
            self.clients = [{
                "index": 0,
                "client": OpenAI(api_key=self.api_key, base_url=self.base_url),
                "model": self.model,
                "base_url": self.base_url
            }]
        else:
            # Use multi-LLM configuration from Config
            self.clients = []
            if hasattr(Config, "LLM_CONFIGS") and Config.LLM_CONFIGS:
                for idx, cfg in enumerate(Config.LLM_CONFIGS):
                    client = OpenAI(
                        api_key=cfg["api_key"],
                        base_url=cfg["base_url"]
                    )
                    self.clients.append({
                        "index": idx + 1,
                        "client": client,
                        "model": cfg["model_name"],
                        "base_url": cfg["base_url"]
                    })
            
            # Fallback to single legacy config if LLM_CONFIGS is empty
            if not self.clients:
                self.api_key = Config.LLM_API_KEY
                self.base_url = Config.LLM_BASE_URL
                self.model = Config.LLM_MODEL_NAME
                
                if not self.api_key:
                    raise ValueError("LLM_API_KEY is not configured")
                    
                self.clients = [{
                    "index": 0,
                    "client": OpenAI(api_key=self.api_key, base_url=self.base_url),
                    "model": self.model,
                    "base_url": self.base_url
                }]
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Send a chat completion request using a randomly selected client.

        Args:
            messages: List of chat messages.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.
            response_format: Optional OpenAI response_format (e.g. JSON mode).

        Returns:
            The model response text.
        """
        # Randomly select a client and its associated model
        cfg = random.choice(self.clients)
        client = cfg["client"]
        model = cfg["model"]
        
        logger.info(f"Using LLM config [{cfg['index']}] model={model} (base_url={cfg['base_url']})")
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # Some models (e.g. MiniMax M2.5) include <think>...</think> content that should be stripped
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send a chat completion request and parse the response as JSON.

        Args:
            messages: List of chat messages.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Parsed JSON object.
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # Strip optional surrounding Markdown code fences
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON returned by LLM: {cleaned_response}")

