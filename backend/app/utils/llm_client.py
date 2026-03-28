import json
import re
import random
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config
from .logger import get_logger

logger = get_logger('mirofish.llm_client')

# Import cost tracker (lazy import to avoid circular dependencies)
_cost_tracker = None

def get_cost_tracker():
    """Lazy load cost tracker to avoid circular imports"""
    global _cost_tracker
    if _cost_tracker is None:
        try:
            from ..services.llm_cost_tracker import LLMCostTracker
            _cost_tracker = LLMCostTracker()
        except Exception as e:
            logger.debug(f"Cost tracker unavailable: {e}")
            _cost_tracker = False  # Mark as tried but failed
    return _cost_tracker if _cost_tracker else None


class LLMClient:
    """Lightweight LLM client supporting multiple providers."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        self.user_id = user_id
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
        response_format: Optional[Dict] = None,
        operation_name: Optional[str] = None,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> str:
        """
        Send a chat completion request using a randomly selected client.

        Args:
            messages: List of chat messages.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.
            response_format: Optional OpenAI response_format (e.g. JSON mode).
            operation_name: Optional operation name for cost tracking (ontology_generation, entity_discovery, etc.)
            project_id: Optional project ID for cost tracking (for project-level operations)
            simulation_id: Optional simulation ID for cost tracking (for simulation-level operations)

        Returns:
            The model response text.
        """
        # Randomly select a client and its associated model
        cfg = random.choice(self.clients)
        client = cfg["client"]
        model = cfg["model"]
        provider = self._get_provider_name(cfg["base_url"])
        
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
        
        # Track token usage if parameters provided
        if operation_name and (project_id or simulation_id):
            self._track_token_usage(
                operation_name=operation_name,
                model=model,
                provider=provider,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                project_id=project_id,
                simulation_id=simulation_id,
                user_id=self.user_id
            )
        
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        operation_name: Optional[str] = None,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request and parse the response as JSON.

        Args:
            messages: List of chat messages.
            temperature: Sampling temperature.
            max_tokens: Maximum number of tokens to generate.
            operation_name: Optional operation name for cost tracking
            project_id: Optional project ID for cost tracking
            simulation_id: Optional simulation ID for cost tracking

        Returns:
            Parsed JSON object.
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            operation_name=operation_name,
            project_id=project_id,
            simulation_id=simulation_id
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
    
    def _get_provider_name(self, base_url: str) -> str:
        """Extract provider name from base URL"""
        if "mistral" in base_url.lower():
            return "mistral"
        elif "openai" in base_url.lower():
            return "openai"
        elif "anthropic" in base_url.lower():
            return "anthropic"
        else:
            return "unknown"
    
    def _track_token_usage(
        self,
        operation_name: str,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        project_id: Optional[str] = None,
        simulation_id: Optional[str] = None,
        user_id: Optional[str] = None 
    ):
        """Track LLM token usage to Supabase"""
        try:
            tracker = get_cost_tracker()
            if tracker:
                result = tracker.track_llm_call(
                    operation_name=operation_name,
                    model=model,
                    provider=provider,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    project_id=project_id,
                    simulation_id=simulation_id,
                    user_id=user_id or self.user_id
                )
                if not result.get("success"):
                    logger.debug(f"Token tracking: {result.get('error')}")
        except Exception as e:
            logger.debug(f"Failed to track LLM usage: {e}")