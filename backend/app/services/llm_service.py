import json
from typing import Dict, Any
from openai import AsyncOpenAI
from app.config import settings

class LLMService:
    """LLM服务"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        self.model = settings.LLM_MODEL

    async def generate(self, prompt: str, system_prompt: str = None) -> str:
        """生成文本"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )

        return response.choices[0].message.content

    async def generate_json(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """生成JSON格式响应"""
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
