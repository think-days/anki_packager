import json
import re
import logging
from typing import Dict, Any
from openai import OpenAI
from anki_packager.prompt import PROMPT

logger = logging.getLogger(__name__)

class OpenRouter:
    def __init__(self, api_key: str, api_base: str, model: str = "openai/gpt-4.1-mini"):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key,
        )

    def explain(self, word: str) -> Dict[str, any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": word},
                ],
                temperature=0.1,
                max_tokens=3000,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )
            
            content = response.choices[0].message.content
            
            # 直接尝试解析JSON，不做复杂清洗
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed for '{word}': {e}")
                
                # 如果JSON解析失败，记录原始内容并返回默认结构
                try:
                    with open("config/ai_failed_json.txt", "a", encoding="utf-8") as f:
                        f.write(f"\n\n=== OpenRouter AI Failed JSON for '{word}' ===\n")
                        f.write(f"Error: {e}\n")
                        f.write(f"Content: {content}\n")
                        f.write("=" * 50 + "\n")
                except:
                    pass
                
                return self.get_default_structure(word)
                        
        except Exception as e:
            logger.error(f"OpenRouter AI request failed for '{word}': {e}")
            return self.get_default_structure(word)

    def try_fix_json_common_errors(self, s):
        """修复常见的JSON格式错误"""
        # 修复字段名错误
        s = s.replace('"ettymology":', '"etymology":')
        
        # 修复中文引号问题 - 将中文引号替换为英文引号
        s = s.replace('"', '"').replace('"', '"')
        s = s.replace(''', "'").replace(''', "'")
        
        # 修复缺少逗号的问题
        # 在对象属性之间添加逗号
        s = re.sub(r'("(?:word|etymology|associative|homophone|tenses|discrimination|english|chinese)"\s*:\s*"[^"]*")\s*("(?:word|etymology|associative|homophone|tenses|discrimination|english|chinese)"\s*:\s*"[^"]*")', r'\1, \2', s)
        
        # 修复mnemonic对象中缺少逗号的问题
        s = re.sub(r'("(?:associative|homophone)"\s*:\s*"[^"]*")\s*("(?:associative|homophone)"\s*:\s*"[^"]*")', r'\1, \2', s)
        
        # 修复对象之间缺少逗号
        s = s.replace('}{', '},{')
        s = s.replace('}{', '},{')
        
        # 修复多余的逗号
        s = re.sub(r',(\s*[}\]])', r'\1', s)
        
        # 修复单引号为双引号
        s = re.sub(r'(?<!\\)"', '"', s)
        
        return s

    def extract_content_by_patterns(self, text, word):
        """最健壮的内容提取：多模式正则+关键词兜底+内容清洗"""
        def pick_first_nonempty(*args):
            for a in args:
                if a and a.strip():
                    return a.strip()
            return ''
        
        def clean(s):
            if not s: return ''
            s = re.sub(r'[\u3000\xa0]+', '', s)  # 去除全角空格等
            s = re.sub(r'[\r\n]+', '\n', s)
            s = re.sub(r'^[\s\-:：、，。]+', '', s)
            s = re.sub(r'[\s\-:：、，。]+$', '', s)
            s = s.strip()
            return s
        
        result = {
            "word": word,
            "origin": {
                "etymology": "",
                "mnemonic": {
                    "associative": "",
                    "homophone": ""
                }
            },
            "tenses": "",
            "discrimination": "",
            "story": {
                "english": "",
                "chinese": ""
            }
        }
        
        try:
            # 词源提取 - 多种模式
            etymology_patterns = [
                r'"etymology":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"etymology":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'词源[：:]\s*([^。\n]+)',
                r'词源[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
                r'etymology[：:]\s*([^。\n]+)',
            ]
            
            for pattern in etymology_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["origin"]["etymology"] = clean(match.group(1))
                    break
            
            # 联想记忆提取
            associative_patterns = [
                r'"associative":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"associative":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'联想[：:]\s*([^。\n]+)',
                r'联想记忆[：:]\s*([^。\n]+)',
                r'associative[：:]\s*([^。\n]+)',
            ]
            
            for pattern in associative_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["origin"]["mnemonic"]["associative"] = clean(match.group(1))
                    break
            
            # 谐音记忆提取
            homophone_patterns = [
                r'"homophone":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"homophone":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'谐音[：:]\s*([^。\n]+)',
                r'谐音记忆[：:]\s*([^。\n]+)',
                r'homophone[：:]\s*([^。\n]+)',
            ]
            
            for pattern in homophone_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["origin"]["mnemonic"]["homophone"] = clean(match.group(1))
                    break
            
            # 词形变化提取
            tenses_patterns = [
                r'"tenses":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"tenses":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'词形[：:]\s*([^。\n]+)',
                r'词形变化[：:]\s*([^。\n]+)',
                r'tenses[：:]\s*([^。\n]+)',
            ]
            
            for pattern in tenses_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["tenses"] = clean(match.group(1))
                    break
            
            # 辨析提取
            discrimination_patterns = [
                r'"discrimination":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"discrimination":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'辨析[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
                r'词语辨析[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
                r'discrimination[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
            ]
            
            for pattern in discrimination_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["discrimination"] = clean(match.group(1))
                    break
            
            # 英文故事提取
            english_story_patterns = [
                r'"english":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"english":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'english[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
            ]
            
            for pattern in english_story_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["story"]["english"] = clean(match.group(1))
                    break
            
            # 中文故事提取
            chinese_story_patterns = [
                r'"chinese":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]',
                r'"chinese":\s*"([^"]*(?:"[^"]*"[^"]*)*)"',
                r'chinese[：:]\s*([^。\n]*(?:。[^。\n]*)*)',
            ]
            
            for pattern in chinese_story_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    result["story"]["chinese"] = clean(match.group(1))
                    break
            
            # 如果某些字段为空，使用默认内容
            if not result["origin"]["etymology"]:
                result["origin"]["etymology"] = f"单词 {word} 的词源信息暂时无法获取。"
            if not result["origin"]["mnemonic"]["associative"]:
                result["origin"]["mnemonic"]["associative"] = f"联想记忆：{word} 的相关联想暂时无法生成。"
            if not result["origin"]["mnemonic"]["homophone"]:
                result["origin"]["mnemonic"]["homophone"] = f"谐音记忆：{word} 的谐音记忆暂时无法生成。"
            if not result["tenses"]:
                result["tenses"] = f"{word} 的词形变化暂时无法获取。"
            if not result["discrimination"]:
                result["discrimination"] = f"单词 {word} 的辨析内容暂时无法获取。"
            if not result["story"]["english"]:
                result["story"]["english"] = f"A story about {word} is temporarily unavailable."
            if not result["story"]["chinese"]:
                result["story"]["chinese"] = f"关于 {word} 的故事暂时无法获取。"
            
            logger.info(f"Successfully extracted content for '{word}' using pattern matching")
            return result
            
        except Exception as e:
            logger.error(f"Pattern extraction failed for '{word}': {e}")
            return self.get_default_structure(word)

    def get_default_structure(self, word):
        """返回默认的AI内容结构"""
        return {
            "word": word,
            "origin": {
                "etymology": f"单词 {word} 的词源信息暂时无法获取。",
                "mnemonic": {
                    "associative": f"联想记忆：{word} 的相关联想暂时无法生成。",
                    "homophone": f"谐音记忆：{word} 的谐音记忆暂时无法生成。"
                }
            },
            "tenses": f"{word} 的词形变化暂时无法获取。",
            "discrimination": f"单词 {word} 的辨析内容暂时无法获取。",
            "story": {
                "english": f"A story about {word} is temporarily unavailable.",
                "chinese": f"关于 {word} 的故事暂时无法获取。"
            }
        } 