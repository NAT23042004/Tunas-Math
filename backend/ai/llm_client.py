from collections.abc import AsyncGenerator
from typing import Any

from litellm import acompletion

from config import settings


class LLMClient:
    """Multi-provider LLM client using LiteLLM"""

    def __init__(self):
        self.provider = getattr(settings, "llm_provider", "anthropic")
        self.model = getattr(settings, "llm_model", "claude-sonnet-4-6")

        # Get API key with fallback to provider-specific keys
        llm_api_key = getattr(settings, "llm_api_key", None)
        if llm_api_key:
            self.api_key = llm_api_key
        else:
            # Fallback to provider-specific keys
            provider_key_map = {
                "anthropic": getattr(settings, "anthropic_api_key", ""),
                "openai": getattr(settings, "openai_api_key", ""),
                "qwen": getattr(settings, "qwen_api_key", ""),
                "gemini": getattr(settings, "gemini_api_key", ""),
                "cohere": getattr(settings, "cohere_api_key", ""),
                "azure": getattr(settings, "azure_api_key", ""),
            }
            self.api_key = provider_key_map.get(self.provider, "")

        # Map provider to model format
        self.model_mapping = {
            "anthropic": f"anthropic/{self.model}",
            "openai": f"openai/{self.model}",
            "cohere": f"cohere/{self.model}",
            "azure": f"azure/{self.model}",
            "qwen": f"qwen/{self.model}",
            "gemini": f"gemini/{self.model}",
        }

    def _get_model_name(self) -> str:
        """Get the properly formatted model name for the provider"""
        provider_prefix = {
            "anthropic": "anthropic",
            "openai": "openai",
            "cohere": "cohere",
            "azure": "azure",
            "qwen": "qwen",
            "gemini": "gemini",
        }.get(self.provider, "")

        if provider_prefix:
            return f"{provider_prefix}/{self.model}"
        return self.model

    async def stream_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """Stream response from LLM API

        Args:
            messages: Conversation history
            system_prompt: System prompt for LLM
            tools: Optional tool definitions
            max_tokens: Maximum tokens in response

        Yields:
            Streamed text chunks
        """
        try:
            model_name = self._get_model_name()

            # Prepare messages with system prompt
            litellm_messages = messages.copy()
            if system_prompt:
                litellm_messages.insert(0, {"role": "system", "content": system_prompt})

            # Stream response
            response = await acompletion(
                model_name=model_name,
                messages=litellm_messages,
                tools=tools,
                max_tokens=max_tokens,
                api_key=self.api_key,
                stream=True,
            )

            async for chunk in response:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content

        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

    async def get_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """Get complete response from LLM API

        Args:
            messages: Conversation history
            system_prompt: System prompt for LLM
            tools: Optional tool definitions
            max_tokens: Maximum tokens in response

        Returns:
            Complete response text
        """
        try:
            model_name = self._get_model_name()

            # Prepare messages with system prompt
            litellm_messages = messages.copy()
            if system_prompt:
                litellm_messages.insert(0, {"role": "system", "content": system_prompt})

            response = await acompletion(
                model_name=model_name,
                messages=litellm_messages,
                tools=tools,
                max_tokens=max_tokens,
                api_key=self.api_key,
            )

            # Extract text from response
            if hasattr(response, "choices") and response.choices:
                return response.choices[0].message.content
            else:
                return str(response)

        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

    async def get_response_with_tools(
        self, messages: list[dict[str, str]], system_prompt: str, tools: list[dict[str, Any]], max_tokens: int = 1024
    ) -> dict[str, Any]:
        """Get response from LLM API with tool use

        Args:
            messages: Conversation history
            system_prompt: System prompt for LLM
            tools: Tool definitions
            max_tokens: Maximum tokens in response

        Returns:
            Response with text and tool calls
        """
        try:
            model_name = self._get_model_name()

            # Prepare messages with system prompt
            litellm_messages = messages.copy()
            if system_prompt:
                litellm_messages.insert(0, {"role": "system", "content": system_prompt})

            response = await acompletion(
                model_name=model_name,
                messages=litellm_messages,
                tools=tools,
                max_tokens=max_tokens,
                api_key=self.api_key,
            )

            result = {"text": "", "tool_calls": []}

            # Extract content and tool calls
            if hasattr(response, "choices") and response.choices:
                message = response.choices[0].message

                # Get text content
                if hasattr(message, "content") and message.content:
                    result["text"] = message.content

                # Get tool calls
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        result["tool_calls"].append(
                            {"id": tool_call.id, "name": tool_call.function.name, "input": tool_call.function.arguments}
                        )

            return result

        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

    def set_provider(self, provider: str, model: str = None, api_key: str = None):
        """Change the LLM provider dynamically

        Args:
            provider: Provider name (anthropic, openai, cohere, azure)
            model: Optional model name
            api_key: Optional API key
        """
        self.provider = provider
        if model:
            self.model = model
        if api_key:
            self.api_key = api_key

    def get_available_providers(self) -> list[str]:
        """Get list of available providers"""
        return list(self.model_mapping.keys())


# Global LLM client instance
llm_client = LLMClient()

# Keep backward compatibility with old code
claude_client = llm_client
