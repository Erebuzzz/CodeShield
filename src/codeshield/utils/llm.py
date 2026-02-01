"""
LLM Utility - Multi-provider AI integration

Supports:
- CometAPI (primary, free tier)
- Novita.ai (fallback, cheap)
- AI/ML API (last resort)
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


class LLMClient:
    """Multi-provider LLM client with automatic fallback"""
    
    PROVIDERS = {
        "cometapi": {
            "base_url": "https://api.cometapi.com/v1",
            "env_key": "COMETAPI_KEY",
            "default_model": "deepseek-chat",  # Free model
            "free_models": ["deepseek-chat", "deepseek-reasoner", "llama-4-maverick"],
        },
        "aiml": {
            "base_url": "https://api.aimlapi.com/v1",
            "env_key": "AIML_API_KEY",
            "default_model": "gpt-4o-mini",
        },
    }
    
    def __init__(self, preferred_provider: Optional[str] = None):
        self.preferred_provider = preferred_provider
        self._client = httpx.Client(timeout=60.0)
    
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
        
        try:
            # Use httpx directly (most reliable)
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
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=provider_name,
                model=model or config["default_model"],
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
            )
        except Exception as e:
            print(f"LLM error ({provider_name}): {e}")
            # Try next provider
            if provider_name == "cometapi":
                return self._try_aiml(prompt, system_prompt, model, max_tokens)
            return None
    
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
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider="aiml",
                model=model or config["default_model"],
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
            )
        except Exception as e:
            print(f"AIML error: {e}")
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
