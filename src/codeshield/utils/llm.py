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
import time
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
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


# Track provider usage for observability
_provider_stats = {
    "cometapi": {"calls": 0, "errors": 0, "tokens": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": 0},
    "novita": {"calls": 0, "errors": 0, "tokens": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": 0},
    "aiml": {"calls": 0, "errors": 0, "tokens": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": 0},
}


def get_provider_stats() -> dict:
    """Get usage statistics for all LLM providers with efficiency metrics"""
    stats = {}
    for provider, data in _provider_stats.items():
        stats[provider] = data.copy()
        # Calculate efficiency metrics
        if data["input_tokens"] > 0:
            stats[provider]["token_efficiency"] = round(data["output_tokens"] / data["input_tokens"], 3)
        else:
            stats[provider]["token_efficiency"] = 0.0
        if data["calls"] > 0:
            stats[provider]["avg_tokens_per_call"] = round(data["tokens"] / data["calls"], 1)
            stats[provider]["avg_latency_ms"] = round(data["latency_ms"] / data["calls"], 1)
            stats[provider]["error_rate"] = round((data["errors"] / data["calls"]) * 100, 2)
        else:
            stats[provider]["avg_tokens_per_call"] = 0.0
            stats[provider]["avg_latency_ms"] = 0.0
            stats[provider]["error_rate"] = 0.0
    return stats


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
        
        # Track call attempt and timing
        _provider_stats[provider_name]["calls"] += 1
        start_time = time.time()
        
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
            
            # Extract token usage with efficiency tracking
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Update provider stats
            _provider_stats[provider_name]["tokens"] += total_tokens
            _provider_stats[provider_name]["input_tokens"] += input_tokens
            _provider_stats[provider_name]["output_tokens"] += output_tokens
            _provider_stats[provider_name]["latency_ms"] += latency_ms
            
            # Track in metrics system
            try:
                from codeshield.utils.metrics import get_metrics
                get_metrics().track_tokens(provider_name, input_tokens, output_tokens, success=True)
            except ImportError:
                pass
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                provider=provider_name,
                model=model or config["default_model"],
                tokens_used=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
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
        """Generate code fix using LLM - MAXIMUM TOKEN EFFICIENCY"""
        from codeshield.utils.token_optimizer import (
            get_token_optimizer, optimize_fix_prompt, 
            LocalProcessor, ModelTier, get_optimal_max_tokens
        )
        
        optimizer = get_token_optimizer()
        
        # 1. TRY LOCAL FIX FIRST (0 tokens!)
        local_fix = LocalProcessor.fix_locally(code, issues)
        if local_fix is not None:
            if not hasattr(optimizer, '_local_saves'):
                optimizer._local_saves = 0
            optimizer._local_saves += 1
            return local_fix
        
        # 2. Generate optimized prompt
        prompt = optimize_fix_prompt(code, issues)
        
        # Check if local fix was signaled
        if prompt == "__LOCAL_FIX__":
            return LocalProcessor.fix_locally(code, issues)
        
        system_prompt = "Fix code. Return code only."  # Ultra short
        
        # 3. Check cache
        cached = optimizer.get_cached(prompt, system_prompt)
        if cached:
            return cached.content
        
        # 4. Calculate optimal max_tokens (dynamic based on code size)
        max_tokens = get_optimal_max_tokens("fix", len(code))
        
        # 5. Check budget
        estimated = optimizer.estimate_tokens(prompt) + max_tokens
        if not optimizer.check_budget(estimated):
            print("Token budget exceeded")
            return None
        
        # 6. Select optimal model for task complexity
        provider_info = self._get_available_provider()
        if provider_info:
            provider_name = provider_info[0]
            optimal_model = ModelTier.select_model(code, issues, provider_name)
        else:
            optimal_model = None
        
        response = self.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            model=optimal_model,
            max_tokens=max_tokens,
        )
        
        if response:
            # Cache the response
            optimizer.cache_response(prompt, response, system_prompt)
            optimizer.record_usage(response.tokens_used)
            
            # Extract code from response
            content = response.content
            if "```python" in content:
                content = content.split("```python")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return content.strip()
        return None
    
    def generate_context_briefing(self, context: dict) -> Optional[str]:
        """Generate context briefing - MAXIMUM TOKEN EFFICIENCY"""
        from codeshield.utils.token_optimizer import (
            get_token_optimizer, optimize_context_prompt, get_optimal_max_tokens
        )
        
        optimizer = get_token_optimizer()
        
        # Use optimized prompt
        prompt = optimize_context_prompt(context)
        
        # Check cache
        cached = optimizer.get_cached(prompt)
        if cached:
            return cached.content
        
        # Dynamic max_tokens (very short for briefings)
        max_tokens = get_optimal_max_tokens("briefing", 0)
        
        response = self.chat(prompt=prompt, max_tokens=max_tokens)
        
        if response:
            optimizer.cache_response(prompt, response)
            optimizer.record_usage(response.tokens_used)
            return response.content
        return None


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
