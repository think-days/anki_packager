import json
from openai import OpenAI
from anki_packager.prompt import prompts
from anki_packager.logger import logger

class SiliconFlow:
    def __init__(self, model: str, api_key: str, api_base: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=api_base)

    def explain(self, word: str):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["siliconflow"]},
                    {"role": "user", "content": word},
                ],
            )
            result = response.choices[0].message.content
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "")
            return json.loads(result)
        except Exception as e:
            logger.error(f"Failed to get {self.model}'s AI explanation: {e}")
            return None
