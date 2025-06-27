from anki_packager.ai.siliconflow import SiliconFlow
from anki_packager.ai.openrouter import OpenRouter

MODEL_DICT = {
    "Pro/deepseek-ai/DeepSeek-V3": SiliconFlow,
    "openai/gpt-4.1-mini": OpenRouter,
    "openai/gpt-4.1-nano": OpenRouter,
}
