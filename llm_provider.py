import os
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import config
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        pass
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
class FoundryLocalProvider(BaseLLMProvider):
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.foundry_model_name
        self._mgr = None
        self._model = None
        self._chat_client = None
        self._init_sdk()

    def _init_sdk(self):
        try:
            from foundry_local_sdk import FoundryLocalManager, Configuration
            if not FoundryLocalManager.instance:
                FoundryLocalManager.initialize(Configuration(app_name="NovaRAG"))
            self._mgr = FoundryLocalManager.instance
            
            self._model = self._mgr.catalog.get_model(self.model_name)
            if not self._model:
                raise RuntimeError(f"Model '{self.model_name}' not found in catalog.")
                
            if not self._model.is_cached:
                print(f"[INFO] Downloading model {self.model_name}. This may take a while...")
                self._model.download()
                
            self._model.load()
            self._chat_client = self._model.get_chat_client()
        except Exception as e:
            raise RuntimeError(f"Microsoft Foundry Local SDK unavailable or failed: {e}")

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if not self._chat_client:
            raise RuntimeError("Foundry Local model is not loaded.")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Question & Context:\n{user_prompt}"}
        ]
        response = self._chat_client.complete_chat(messages=messages)
        return str(response.choices[0].message.content)

    @property
    def provider_name(self) -> str:
        return f"Microsoft Foundry Local ({self.model_name})"
class LocalOpenAIProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or config.openai_base_url).rstrip('/')
        self.api_key = api_key or config.api_key if hasattr(config, 'api_key') else 'ollama'
        self._ping()
    def _ping(self):
        url = f"{self.base_url}/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                pass
        except Exception as e:
            raise RuntimeError(f"Local OpenAI endpoint unavailable at {url}: {e}")
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": "phi-3.5-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            raise RuntimeError(f"Local OpenAI endpoint error at {url}: {e}")
    @property
    def provider_name(self) -> str:
        return f"Local OpenAI API ({self.base_url})"
class OfflineFallbackProvider(BaseLLMProvider):
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        if "Context Passages:" not in user_prompt or "No relevant document passages found" in user_prompt:
            return "Maalesef yerel bilgi tabanımda bu soruya dair bir bilgi yok. Başka bir konuda yardım isterseniz buradayım!"
        try:
            context_part = user_prompt.split("Context Passages:")[1].split("Question:")[0].strip()
            passages = [p.strip() for p in context_part.split("\n\n---\n\n") if p.strip()]
        except Exception:
            passages = []
        if not passages:
            return "Maalesef yerel bilgi tabanımda bu soruya dair bir bilgi yok. Başka bir konuda yardım isterseniz buradayım!"
        try:
            combined_lines = []
            for passage in passages:
                content = passage.split("]\n", 1)[1].strip()
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    if line and line not in combined_lines:
                        combined_lines.append(line)
            if combined_lines:
                return "\n\n".join(combined_lines)
            return passages[0].split("]\n", 1)[1].strip()
        except Exception:
            return "Maalesef bu soruya uygun net bir cevap çıkaramadım."
    @property
    def provider_name(self) -> str:
        return "Offline Grounded Engine (Standard Local Fallback)"
def get_llm_provider(mode: str = None) -> BaseLLMProvider:
    mode = mode or config.llm_provider
    if mode == "foundry":
        try:
            return FoundryLocalProvider()
        except Exception as e:
            print(f"[Warning] Foundry Local SDK not ready: {e}. Falling back to Offline Provider.")
            return OfflineFallbackProvider()
    elif mode == "openai":
        try:
            return LocalOpenAIProvider()
        except Exception as e:
            print(f"[Warning] Local OpenAI server unavailable: {e}. Falling back to Offline Provider.")
            return OfflineFallbackProvider()
    elif mode == "auto":
        try:
            return FoundryLocalProvider()
        except Exception:
            pass
        try:
            return LocalOpenAIProvider()
        except Exception:
            pass
    return OfflineFallbackProvider()
