import anthropic
from typing import AsyncGenerator, Optional, Dict, Any, List
from config import settings


class ClaudeClient:
    """Client for interacting with Claude API"""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )
        self.model = "claude-sonnet-4-6"

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024
    ) -> AsyncGenerator[str, None]:
        """Stream response from Claude API

        Args:
            messages: Conversation history
            system_prompt: System prompt for Claude
            tools: Optional tool definitions
            max_tokens: Maximum tokens in response

        Yields:
            Streamed text chunks
        """
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                tools=tools or []
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    async def get_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024
    ) -> str:
        """Get complete response from Claude API

        Args:
            messages: Conversation history
            system_prompt: System prompt for Claude
            tools: Optional tool definitions
            max_tokens: Maximum tokens in response

        Returns:
            Complete response text
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                tools=tools or []
            )
            return response.content[0].text

        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    async def get_response_with_tools(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Get response from Claude API with tool use

        Args:
            messages: Conversation history
            system_prompt: System prompt for Claude
            tools: Tool definitions
            max_tokens: Maximum tokens in response

        Returns:
            Response with text and tool calls
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages,
                tools=tools
            )

            result = {
                "text": "",
                "tool_calls": []
            }

            for content in response.content:
                if content.type == "text":
                    result["text"] = content.text
                elif content.type == "tool_use":
                    result["tool_calls"].append({
                        "id": content.id,
                        "name": content.name,
                        "input": content.input
                    })

            return result

        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")


# Global Claude client instance
claude_client = ClaudeClient()