"""
LLM client tests for Toán Socratic backend
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from ai.llm_client import LLMClient


class TestLLMClient:
    """Test LLM client functionality"""

    @pytest.mark.unit
    def test_client_initialization(self):
        """Test LLM client initialization"""
        client = LLMClient()

        assert client.provider == "anthropic"
        assert client.model == "claude-sonnet-4-6"
        assert client.api_key is not None

    @pytest.mark.unit
    def test_get_model_name(self):
        """Test model name formatting"""
        client = LLMClient()

        # Test Anthropic
        client.provider = "anthropic"
        client.model = "claude-sonnet-4-6"
        assert client._get_model_name() == "anthropic/claude-sonnet-4-6"

        # Test OpenAI
        client.provider = "openai"
        client.model = "gpt-4"
        assert client._get_model_name() == "openai/gpt-4"

        # Test Qwen
        client.provider = "qwen"
        client.model = "qwen-turbo"
        assert client._get_model_name() == "qwen/qwen-turbo"

        # Test Gemini
        client.provider = "gemini"
        client.model = "gemini-pro"
        assert client._get_model_name() == "gemini/gemini-pro"

    @pytest.mark.unit
    def test_get_available_providers(self):
        """Test getting available providers"""
        client = LLMClient()
        providers = client.get_available_providers()

        assert isinstance(providers, list)
        assert "anthropic" in providers
        assert "openai" in providers
        assert "qwen" in providers
        assert "gemini" in providers
        assert "cohere" in providers
        assert "azure" in providers

    @pytest.mark.unit
    def test_set_provider(self):
        """Test dynamic provider switching"""
        client = LLMClient()

        # Switch to OpenAI
        client.set_provider("openai", "gpt-4-turbo")
        assert client.provider == "openai"
        assert client.model == "gpt-4-turbo"

        # Switch to Qwen
        client.set_provider("qwen", "qwen-max")
        assert client.provider == "qwen"
        assert client.model == "qwen-max"

        # Switch with API key
        client.set_provider("gemini", "gemini-pro", "test-api-key")
        assert client.provider == "gemini"
        assert client.model == "gemini-pro"
        assert client.api_key == "test-api-key"


class TestLLMClientResponses:
    """Test LLM client response methods"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_response(self):
        """Test getting complete response"""
        client = LLMClient()

        messages = [
            {"role": "user", "content": "Test message"}
        ]
        system_prompt = "You are a helpful assistant."

        # Mock the litellm completion
        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test AI response"
            mock_completion.return_value = mock_response

            response = await client.get_response(messages, system_prompt)

            assert response == "Test AI response"
            mock_completion.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_response_with_tools(self):
        """Test getting response with tool calls"""
        client = LLMClient()

        messages = [{"role": "user", "content": "Test message"}]
        system_prompt = "You are a helpful assistant."
        tools = [{"name": "test_tool", "description": "Test tool"}]

        # Mock the litellm completion
        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"

            # Create proper mock for tool_calls
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call-1"
            mock_tool_call.function.name = "test_tool"
            mock_tool_call.function.arguments = '{"param": "value"}'

            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_completion.return_value = mock_response

            result = await client.get_response_with_tools(messages, system_prompt, tools)

            assert result["text"] == "Test response"
            assert len(result["tool_calls"]) == 1
            assert result["tool_calls"][0]["name"] == "test_tool"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_stream_response(self):
        """Test streaming response"""
        client = LLMClient()

        messages = [{"role": "user", "content": "Test message"}]
        system_prompt = "You are a helpful assistant."

        # Mock the streaming completion
        with patch('ai.llm_client.acompletion') as mock_completion:
            # Create mock chunks
            chunk1 = MagicMock()
            chunk1.choices = [MagicMock()]
            chunk1.choices[0].delta.content = "Hello "

            chunk2 = MagicMock()
            chunk2.choices = [MagicMock()]
            chunk2.choices[0].delta.content = "world!"

            # Make it async iterable
            async def mock_stream():
                yield chunk1
                yield chunk2

            mock_completion.return_value = mock_stream()

            # Collect streamed content
            chunks = []
            async for chunk in client.stream_response(messages, system_prompt):
                chunks.append(chunk)

            assert chunks == ["Hello ", "world!"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_response_error_handling(self):
        """Test error handling in get_response"""
        client = LLMClient()

        messages = [{"role": "user", "content": "Test message"}]
        system_prompt = "You are a helpful assistant."

        # Mock an error
        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_completion.side_effect = Exception("API Error")

            with pytest.raises(Exception) as exc_info:
                await client.get_response(messages, system_prompt)

            assert "LLM API error" in str(exc_info.value)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_response_without_choices(self):
        """Test handling response without choices"""
        client = LLMClient()

        messages = [{"role": "user", "content": "Test message"}]
        system_prompt = "You are a helpful assistant."

        # Mock response without choices
        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = []
            mock_completion.return_value = mock_response

            response = await client.get_response(messages, system_prompt)

            # Should return string representation
            assert isinstance(response, str)


class TestLLMClientIntegration:
    """Integration tests for LLM client"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_message_flow(self):
        """Test full message flow with system prompt"""
        client = LLMClient()

        messages = [
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "2+2=4"},
            {"role": "user", "content": "What about 3+3?"}
        ]
        system_prompt = "You are a math tutor."

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "3+3=6"
            mock_completion.return_value = mock_response

            response = await client.get_response(messages, system_prompt)

            assert response == "3+3=6"

            # Verify the call was made with system prompt prepended
            call_args = mock_completion.call_args
            litellm_messages = call_args[1]['messages']
            assert litellm_messages[0]["role"] == "system"
            assert litellm_messages[0]["content"] == system_prompt

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_use_integration(self):
        """Test tool use integration"""
        client = LLMClient()

        messages = [{"role": "user", "content": "Draw a pyramid"}]
        system_prompt = "You are a geometry tutor."
        tools = [{
            "name": "render_geometry",
            "description": "Render 3D geometry",
            "input_schema": {
                "type": "object",
                "properties": {
                    "solid_type": {"type": "string"},
                    "params": {"type": "object"}
                }
            }
        }]

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "I'll draw a pyramid for you."

            # Create proper mock for tool_calls
            mock_tool_call = MagicMock()
            mock_tool_call.id = "call-1"
            mock_tool_call.function.name = "render_geometry"
            mock_tool_call.function.arguments = '{"solid_type": "pyramid", "params": {"base_side": 6}}'

            mock_response.choices[0].message.tool_calls = [mock_tool_call]
            mock_completion.return_value = mock_response

            result = await client.get_response_with_tools(messages, system_prompt, tools)

            assert result["text"] == "I'll draw a pyramid for you."
            assert len(result["tool_calls"]) == 1
            assert result["tool_calls"][0]["name"] == "render_geometry"
            assert "pyramid" in result["tool_calls"][0]["input"]


class TestLLMClientProviders:
    """Test different LLM providers"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_anthropic_provider(self):
        """Test Anthropic provider"""
        client = LLMClient()
        client.set_provider("anthropic", "claude-sonnet-4-6")

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Anthropic response"
            mock_completion.return_value = mock_response

            response = await client.get_response([{"role": "user", "content": "Test"}], "Test")

            assert response == "Anthropic response"
            call_args = mock_completion.call_args
            assert call_args[1]['model_name'] == "anthropic/claude-sonnet-4-6"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_openai_provider(self):
        """Test OpenAI provider"""
        client = LLMClient()
        client.set_provider("openai", "gpt-4")

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "OpenAI response"
            mock_completion.return_value = mock_response

            response = await client.get_response([{"role": "user", "content": "Test"}], "Test")

            assert response == "OpenAI response"
            call_args = mock_completion.call_args
            assert call_args[1]['model_name'] == "openai/gpt-4"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_qwen_provider(self):
        """Test Qwen provider"""
        client = LLMClient()
        client.set_provider("qwen", "qwen-turbo")

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Qwen response"
            mock_completion.return_value = mock_response

            response = await client.get_response([{"role": "user", "content": "Test"}], "Test")

            assert response == "Qwen response"
            call_args = mock_completion.call_args
            assert call_args[1]['model_name'] == "qwen/qwen-turbo"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_gemini_provider(self):
        """Test Gemini provider"""
        client = LLMClient()
        client.set_provider("gemini", "gemini-pro")

        with patch('ai.llm_client.acompletion') as mock_completion:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Gemini response"
            mock_completion.return_value = mock_response

            response = await client.get_response([{"role": "user", "content": "Test"}], "Test")

            assert response == "Gemini response"
            call_args = mock_completion.call_args
            assert call_args[1]['model_name'] == "gemini/gemini-pro"