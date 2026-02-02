"""
LLM Utility - Multi-provider AI integration

Supports (in priority order):
- CometAPI (primary) - OpenAI-compatible unified gateway to 100+ models
  Docs: https://apidoc.cometapi.com/
- Novita.ai (secondary) - Cost-effective open-source model inference
  Docs: https://novita.ai/docs/guides/llm-api
- AI/ML API (fallback)

Provider chain ensures high availability with automatic fallback.
"""

import os
import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    provider: str
    model: str
    tokens_used: int = 0


# Track provider usage for observability
_provider_stats = {
    "cometapi": {"calls": 0, "errors": 0, "tokens": 0},
    "novita": {"calls": 0, "errors": 0, "tokens": 0},
    "aiml": {"calls": 0, "errors": 0, "tokens": 0},
}


def get_provider_stats() -> dict:
    """Get usage statistics for all LLM providers"""
    return _provider_stats.copy()


class LLMClient:
    """
    Multi-provider LLM client with automatic fallback.
    
    Provider Priority:
    1. CometAPI - Unified gateway with free tier models (deepseek-chat)
    2. Novita.ai - OpenAI-compatible API for open-source models
    3. AIML API - Backup provider
    
    All providers use OpenAI-compatible /v1/chat/completions endpoint.
    """
    
    PROVIDERS = {
        "cometapi": {
            "base_url": "https://api.cometapi.com/v1",
            "env_key": "COMETAPI_KEY",
            "default_model": "deepseek-chat",  # Free model on CometAPI
            "free_models": ["deepseek-chat", "deepseek-reasoner", "llama-4-maverick"],
            "description": "CometAPI - Unified AI gateway (100+ models)",
        },
        "novita": {
            "base_url": "https://api.novita.ai/openai/v1",
            "env_key": "NOVITA_API_KEY",
            "default_model": "deepseek/deepseek-r1",  # Strong open-source model
            "free_models": ["meta-llama/llama-3-8b-instruct"],
            "description": "Novita.ai - Cost-effective inference platform",
        },
        "aiml": {
            "base_url": "https://api.aimlapi.com/v1",
            "env_key": "AIML_API_KEY",
            "default_model": "gpt-4o-mini",
            "description": "AIML API - Fallback provider",
        },
    }
    
    def __init__(self, preferred_provider: Optional[str] = None):
        self.preferred_provider = preferred_provider
        self._client = httpx.Client(timeout=60.0)
    
    def get_status(self) -> dict:
        """
        Get status of all configured LLM providers.
        Useful for observability and debugging connectivity.
        """
        status = {}
        for name, config in self.PROVIDERS.items():
            api_key = os.getenv(config["env_key"])
            status[name] = {
                "configured": bool(api_key),
                "env_var": config["env_key"],
                "base_url": config["base_url"],
                "default_model": config["default_model"],
                "description": config.get("description", ""),
                "stats": _provider_stats.get(name, {}),
            }
        return status
    
    def _get_available_provider(self) -> Optional[tuple[str, dict]]:
        """Get first available provider with valid API key"""
        order = [self.preferred_provider] if self.preferred_provider else []
        order.extend(["cometapi", "novita", "aiml"])
        
        for name in order:
            if name and name in self.PROVIDERS:
                config = self.PROVIDERS[name]
                api_key = os.getenv(config["env_key"])
                if api_key:
                    return name, config
        return None
    
    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
    ) -> Optional[LLMResponse]:
        """
        Send chat completion request.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Optional model override
            max_tokens: Maximum tokens in response
        
        Returns:
            LLMResponse or None if all providers fail
        """
        provider_info = self._get_available_provider()
        if not provider_info:
            return None
        
        provider_name, config = provider_info
        api_key = os.getenv(config["env_key"])
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Track call attempt
        _provider_stats[provider_name]["calls"] += 1
        
        try:
            # Use httpx directly (most reliable) - OpenAI-compatible endpoint
            response = self._client.post(
                f"{config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or config["default_model"],
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            tokens = data.get("usage", {}).get("total_tokens", 0)
            _provider_stats[provider_name]["tokens"] += tokens
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=provider_name,
                model=model or config["default_model"],
                tokens_used=tokens,
            )
        except Exception as e:
            print(f"LLM error ({provider_name}): {e}")
            _provider_stats[provider_name]["errors"] += 1
            # Try fallback chain: cometapi -> novita -> aiml
            if provider_name == "cometapi":
                return self._try_novita(prompt, system_prompt, model, max_tokens)
            elif provider_name == "novita":
                return self._try_aiml(prompt, system_prompt, model, max_tokens)
            return None
    
    def _try_novita(self, prompt: str, system_prompt: Optional[str], model: Optional[str], max_tokens: int) -> Optional[LLMResponse]:
        """Fallback to Novita.ai API"""
        config = self.PROVIDERS.get("novita")
        if not config:
            return self._try_aiml(prompt, system_prompt, model, max_tokens)
        
        api_key = os.getenv(config["env_key"])
        if not api_key:
            return self._try_aiml(prompt, system_prompt, model, max_tokens)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        _provider_stats["novita"]["calls"] += 1
        
        try:
            response = self._client.post(
                f"{config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or config["default_model"],
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            tokens = data.get("usage", {}).get("total_tokens", 0)
            _provider_stats["novita"]["tokens"] += tokens
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider="novita",
                model=model or config["default_model"],
                tokens_used=tokens,
            )
        except Exception as e:
            print(f"Novita error: {e}")
            _provider_stats["novita"]["errors"] += 1
            return self._try_aiml(prompt, system_prompt, model, max_tokens)
    
    def _try_aiml(self, prompt: str, system_prompt: Optional[str], model: Optional[str], max_tokens: int) -> Optional[LLMResponse]:
        """Fallback to AIML API"""
        config = self.PROVIDERS.get("aiml")
        if not config:
            return None
        
        api_key = os.getenv(config["env_key"])
        if not api_key:
            return None
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        _provider_stats["aiml"]["calls"] += 1
        
        try:
            response = self._client.post(
                f"{config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model or config["default_model"],
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            tokens = data.get("usage", {}).get("total_tokens", 0)
            _provider_stats["aiml"]["tokens"] += tokens
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider="aiml",
                model=model or config["default_model"],
                tokens_used=tokens,
            )
        except Exception as e:
            print(f"AIML error: {e}")
            _provider_stats["aiml"]["errors"] += 1
            return None
    
    def generate_fix(self, code: str, issues: list[str]) -> Optional[str]:
        """Generate code fix using LLM"""
        issues_text = "\n".join(f"- {issue}" for issue in issues)
        
        prompt = f"""Fix the following Python code issues:

Issues found:
{issues_text}

Original code:
```python
{code}
```

Return ONLY the fixed Python code, no explanations."""
        
        response = self.chat(
            prompt=prompt,
            system_prompt="You are a code fixer. Return only valid Python code.",
            max_tokens=2000,
        )
        
        if response:
            # Extract code from response
            content = response.content
            if "```python" in content:
                content = content.split("```python")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return content.strip()
        return None
    
    def generate_context_briefing(self, context: dict) -> Optional[str]:
        """Generate context briefing for returning developer"""
        prompt = f"""Summarize this coding context in 2-3 sentences for a developer returning to their work:

Context:
- Files open: {context.get('files', [])}
- Last edited: {context.get('last_edited', 'unknown')}
- Recent changes: {context.get('changes', 'none')}
- Cursor position: {context.get('cursor', 'unknown')}

Be conversational, like: "You were working on X. Last change was Y. Next step might be Z."
"""
        
        response = self.chat(prompt=prompt, max_tokens=200)
        return response.content if response else None


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
