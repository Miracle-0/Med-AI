import json
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务 — 封装 OpenAI 兼容 API 调用"""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本（单轮）"""
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.generate_with_messages(messages)

    async def generate_with_messages(self, messages: List[Dict[str, str]]) -> str:
        """生成文本（支持完整消息列表，用于多轮对话）"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """生成 JSON 格式响应"""
        response = await self.generate(prompt, system_prompt)
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_response": response}


llm_service = LLMService()
