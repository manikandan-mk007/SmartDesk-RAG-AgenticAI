import json
import re
from typing import Any

import requests
from django.conf import settings


class LLMProviderError(Exception):
    pass


class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.timeout = settings.AI_TIMEOUT_SECONDS

    def generate_text(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if self.provider == "gemini":
            return self._generate_with_gemini(system_prompt, user_prompt)

        if self.provider == "groq":
            return self._generate_with_groq(system_prompt, user_prompt)

        if self.provider == "auto":
            return self._generate_auto(system_prompt, user_prompt)

        raise LLMProviderError("LLM provider is set to rules only.")

    def _generate_auto(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if settings.GEMINI_API_KEY:
            try:
                return self._generate_with_gemini(system_prompt, user_prompt)
            except Exception:
                pass

        if settings.GROQ_API_KEY:
            try:
                return self._generate_with_groq(system_prompt, user_prompt)
            except Exception:
                pass

        raise LLMProviderError("No working LLM provider available.")

    def _generate_with_gemini(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if not settings.GEMINI_API_KEY:
            raise LLMProviderError("Gemini API key is missing.")

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.GEMINI_MODEL}:generateContent"
            f"?key={settings.GEMINI_API_KEY}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\n{user_prompt}"
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 800,
            },
        }

        response = requests.post(url, json=payload, timeout=self.timeout)

        if response.status_code >= 400:
            raise LLMProviderError(f"Gemini API error: {response.text}")

        data = response.json()

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise LLMProviderError("Invalid Gemini response format.")

        return text, f"gemini:{settings.GEMINI_MODEL}"

    def _generate_with_groq(self, system_prompt: str, user_prompt: str) -> tuple[str, str]:
        if not settings.GROQ_API_KEY:
            raise LLMProviderError("Groq API key is missing.")

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.GROQ_MODEL,
            "temperature": 0.2,
            "max_tokens": 800,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise LLMProviderError(f"Groq API error: {response.text}")

        data = response.json()

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise LLMProviderError("Invalid Groq response format.")

        return text, f"groq:{settings.GROQ_MODEL}"


def extract_json_from_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in LLM response.")

    return json.loads(match.group(0))