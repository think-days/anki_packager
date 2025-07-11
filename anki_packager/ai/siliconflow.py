import json
from typing import Dict
from openai import OpenAI
import re
import demjson3

from anki_packager.prompt import prompts
from anki_packager.logger import logger


class SiliconFlow:
    def __init__(self, model: str, api_key: str, api_base: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=api_base)

    def normalize_ai_result(self, obj):
        if isinstance(obj, dict):
            return {k: self.normalize_ai_result(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return ', '.join([str(self.normalize_ai_result(x)) for x in obj if x is not None])
        elif obj is None:
            return ""
        else:
            return str(obj)

    def clean_invalid_json_escapes(self, s):
        # 先修复所有不完整的\u转义（如\u、\u1、\u12、\u123）
        s = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', s)
        # 只允许合法的JSON转义，其余的\X全部替换为\\X
        def replacer(match):
            esc = match.group(0)
            # 合法的JSON转义
            if re.match(r'\\|\n|\r|\t|\"|\/|\b|\f|\\u[0-9a-fA-F]{4}', esc):
                return esc
            # 其它非法转义，替换为双反斜杠
            return '\\' + esc[1:]
        # 匹配所有 \X
        return re.sub(r'\\.', replacer, s)

    def try_fix_json_common_errors(self, s):
        """修复常见的JSON格式错误 - 更智能的版本"""
        try:
            # 1. 修复字段名错误
            s = s.replace('"ettymology":', '"etymology":')
            
            # 2. 修复中文引号问题 - 更精确的处理
            # 先处理字段值中的中文引号
            def fix_chinese_quotes_in_values(match):
                field_name = match.group(1)
                field_value = match.group(2)
                # 将中文引号替换为英文引号，但保留转义
                field_value = field_value.replace('"', '"').replace('"', '"')
                field_value = field_value.replace(''', "'").replace(''', "'")
                return f'"{field_name}": "{field_value}"'
            
            # 匹配所有字段值并修复中文引号
            s = re.sub(r'"([^"]+)":\s*"([^"]*(?:"[^"]*"[^"]*)*)"', fix_chinese_quotes_in_values, s)
            
            # 3. 修复缺少逗号的问题
            # 在对象属性之间添加逗号
            s = re.sub(r'("(?:word|etymology|associative|homophone|tenses|discrimination|english|chinese)"\s*:\s*"[^"]*")\s*("(?:word|etymology|associative|homophone|tenses|discrimination|english|chinese)"\s*:\s*"[^"]*")', r'\1, \2', s)
            
            # 修复mnemonic对象中缺少逗号的问题
            s = re.sub(r'("(?:associative|homophone)"\s*:\s*"[^"]*")\s*("(?:associative|homophone)"\s*:\s*"[^"]*")', r'\1, \2', s)
            
            # 修复对象之间缺少逗号
            s = s.replace('}{', '},{')
            
            # 4. 修复多余的逗号
            s = re.sub(r',([\s]*[}\]])', r'\1', s)
            
            # 5. 修复字符串中的转义问题
            s = s.replace('\\"', '"')
            s = s.replace('\\\\', '\\')
            
            # 6. 修复换行符
            s = s.replace('\n', '\\n')
            s = s.replace('\r', '\\r')
            
            # 7. 去除多余的空格
            s = re.sub(r'\s+', ' ', s)
            s = s.strip()
            
            # 8. 最后检查：确保JSON结构完整
            # 如果缺少结束的大括号，添加它们
            if s.count('{') > s.count('}'):
                s += '}' * (s.count('{') - s.count('}'))
            
            return s
            
        except Exception as e:
            logger.warning(f"JSON修复过程中出错: {e}")
            return s

    def create_default_ai_structure(self, word):
        """创建一个默认的AI内容结构，用于API调用失败时"""
        return {
            "word": word,
            "origin": {
                "etymology": f"单词 {word} 的词源信息暂时无法获取。",
                "mnemonic": {
                    "associative": f"{word} 的联想记忆暂时无法生成。",
                    "homophone": f"{word} 的谐音记忆暂时无法生成。"
                }
            },
            "tenses": f"{word} 的词形变化暂时无法获取。",
            "discrimination": f"{word} 的辨析内容暂时无法获取。",
            "definition": f"The definition for {word} is temporarily unavailable.",
            "story": {
                "english": f"A story about {word} is temporarily unavailable.",
                "chinese": f"关于 {word} 的故事暂时无法获取。"
            },
            "phrases": [
                {
                    "english": f"{word}",
                    "chinese": f"{word}的常用短语暂时无法获取"
                }
            ],
            "sentences": [
                {
                    "english": f"Example sentence with {word} is unavailable.",
                    "chinese": f"包含{word}的例句暂时无法获取",
                    "source": ""
                }
            ]
        }

    def extract_ai_content_directly(self, text, word):
        """直接从AI返回的文本中提取内容，不依赖JSON解析"""
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
            "definition": "",
            "story": {
                "english": "",
                "chinese": ""
            }
        }
        
        # 清理文本，移除重复的内容
        text = self.clean_duplicated_content(text)
        
        try:
            # 使用更宽松的正则表达式来提取内容，支持中文引号
            # 提取etymology - 支持多行内容，取第一个匹配
            etymology_pattern = r'"etymology":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            etymology_matches = re.findall(etymology_pattern, text, re.DOTALL)
            if etymology_matches:
                result["origin"]["etymology"] = self.clean_content(etymology_matches[0])
            
            # 提取associative - 支持多行内容，取第一个匹配
            associative_pattern = r'"associative":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            associative_matches = re.findall(associative_pattern, text, re.DOTALL)
            if associative_matches:
                result["origin"]["mnemonic"]["associative"] = self.clean_content(associative_matches[0])
            
            # 提取homophone - 支持多行内容，取第一个匹配
            homophone_pattern = r'"homophone":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            homophone_matches = re.findall(homophone_pattern, text, re.DOTALL)
            if homophone_matches:
                result["origin"]["mnemonic"]["homophone"] = self.clean_content(homophone_matches[0])
            
            # 提取tenses - 支持多行内容，取第一个匹配
            tenses_pattern = r'"tenses":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            tenses_matches = re.findall(tenses_pattern, text, re.DOTALL)
            if tenses_matches:
                result["tenses"] = self.clean_content(tenses_matches[0])
            
            # 提取discrimination - 支持多行内容，取第一个匹配
            discrimination_pattern = r'"discrimination":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            discrimination_matches = re.findall(discrimination_pattern, text, re.DOTALL)
            if discrimination_matches:
                result["discrimination"] = self.clean_content(discrimination_matches[0])
                
            # 提取definition (英文释义) - 支持多行内容，取第一个匹配
            definition_pattern = r'"definition":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            definition_matches = re.findall(definition_pattern, text, re.DOTALL)
            if definition_matches:
                result["definition"] = self.clean_content(definition_matches[0])
            
            # 提取story english - 支持多行内容，取第一个匹配
            story_en_pattern = r'"english":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            story_en_matches = re.findall(story_en_pattern, text, re.DOTALL)
            if story_en_matches:
                result["story"]["english"] = self.clean_content(story_en_matches[0])
            
            # 提取story chinese - 支持多行内容，取第一个匹配
            story_cn_pattern = r'"chinese":\s*[""]([^""]*(?:[""][^""]*[""][^""]*)*)[""]'
            story_cn_matches = re.findall(story_cn_pattern, text, re.DOTALL)
            if story_cn_matches:
                result["story"]["chinese"] = self.clean_content(story_cn_matches[0])
            
            # 如果正则提取失败，尝试使用更宽松的模式匹配
            if not any([result["origin"]["etymology"], result["origin"]["mnemonic"]["associative"], 
                       result["origin"]["mnemonic"]["homophone"], result["tenses"], 
                       result["discrimination"], result["definition"], result["story"]["english"], result["story"]["chinese"]]):
                result = self.extract_content_by_patterns(text, word)
                
        except Exception as e:
            logger.warning(f"直接提取AI内容时出错: {e}")
            # 如果所有方法都失败，使用模式匹配作为最后的备选方案
            result = self.extract_content_by_patterns(text, word)
        
        return result

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
            "definition": "",
            "story": {
                "english": "",
                "chinese": ""
            }
        }
        # 词源
        ety = pick_first_nonempty(
            re.search(r'词源[：: ]*([\s\S]{5,300}?)((?:助记|联想|谐音|词形|辨析|英文释义|故事|$))', text),
            re.search(r'etymology[：: ]*([\s\S]{5,300}?)((?:mnemonic|associative|homophone|tenses|discrimination|definition|story|$))', text, re.I),
            re.search(r'来源[：: ]*([\s\S]{5,300}?)((?:助记|联想|谐音|词形|辨析|英文释义|故事|$))', text),
            re.search(r'源自[\s\S]{5,100}', text)
        )
        if isinstance(ety, re.Match): ety = ety.group(1)
        result["origin"]["etymology"] = clean(ety)
        
        # 联想记忆
        assoc = pick_first_nonempty(
            re.search(r'联想[：: ]*([\s\S]{5,300}?)((?:谐音|词形|辨析|英文释义|故事|$))', text),
            re.search(r'associative[：: ]*([\s\S]{5,300}?)((?:homophone|tenses|discrimination|definition|story|$))', text, re.I)
        )
        if isinstance(assoc, re.Match): assoc = assoc.group(1)
        result["origin"]["mnemonic"]["associative"] = clean(assoc)
        
        # 谐音记忆
        homo = pick_first_nonempty(
            re.search(r'谐音[：: ]*([\s\S]{5,300}?)((?:词形|辨析|英文释义|故事|$))', text),
            re.search(r'homophone[：: ]*([\s\S]{5,300}?)((?:tenses|discrimination|definition|story|$))', text, re.I)
        )
        if isinstance(homo, re.Match): homo = homo.group(1)
        result["origin"]["mnemonic"]["homophone"] = clean(homo)
        
        # 词形变化
        tenses = pick_first_nonempty(
            re.search(r'词形[：: ]*([\s\S]{5,300}?)((?:辨析|英文释义|故事|$))', text),
            re.search(r'tenses[：: ]*([\s\S]{5,300}?)((?:discrimination|definition|story|$))', text, re.I),
            re.search(r'时态[：: ]*([\s\S]{5,300}?)((?:辨析|英文释义|故事|$))', text)
        )
        if isinstance(tenses, re.Match): tenses = tenses.group(1)
        result["tenses"] = clean(tenses)
        
        # 辨析
        discr = pick_first_nonempty(
            re.search(r'辨析[：: ]*([\s\S]{5,500}?)((?:英文释义|故事|$))', text),
            re.search(r'discrimination[：: ]*([\s\S]{5,500}?)((?:definition|story|$))', text, re.I),
            re.search(r'区别[：: ]*([\s\S]{5,500}?)((?:英文释义|故事|$))', text)
        )
        if isinstance(discr, re.Match): discr = discr.group(1)
        result["discrimination"] = clean(discr)
        
        # 英文释义
        defn = pick_first_nonempty(
            re.search(r'英文释义[：: ]*([\s\S]{5,500}?)((?:故事|$))', text),
            re.search(r'definition[：: ]*([\s\S]{5,500}?)((?:story|phrases|sentences|$))', text, re.I),
            re.search(r'英文定义[：: ]*([\s\S]{5,500}?)((?:故事|$))', text)
        )
        if isinstance(defn, re.Match): defn = defn.group(1)
        result["definition"] = clean(defn)
        
        # 英文故事
        story_en = pick_first_nonempty(
            re.search(r'english[：: ]*([\s\S]{10,400}?)((?:chinese|$))', text, re.I),
            re.search(r'故事[（(（英][：: ]*([\s\S]{10,400}?)((?:中文|$))', text),
            re.search(r'(In\s+[A-Z][^\n]+[\s\S]{10,400})', text),
            re.search(r'(On\s+[A-Z][^\n]+[\s\S]{10,400})', text)
        )
        if isinstance(story_en, re.Match): story_en = story_en.group(1)
        result["story"]["english"] = clean(story_en)
        
        # 中文故事
        story_cn = pick_first_nonempty(
            re.search(r'chinese[：: ]*([\s\S]{10,400})', text, re.I),
            re.search(r'故事[（(（中][：: ]*([\s\S]{10,400})', text),
            re.search(r'在[\u4e00-\u9fa5][^\n]{10,400}', text)
        )
        if isinstance(story_cn, re.Match): story_cn = story_cn.group(1)
        result["story"]["chinese"] = clean(story_cn)
        
        # 兜底：如果某字段为空，填"暂时无法获取"
        if not result["origin"]["etymology"]:
            result["origin"]["etymology"] = "该单词的词源信息暂时无法获取。"
        if not result["origin"]["mnemonic"]["associative"]:
            result["origin"]["mnemonic"]["associative"] = f"{word} 的联想记忆暂时无法生成。"
        if not result["origin"]["mnemonic"]["homophone"]:
            result["origin"]["mnemonic"]["homophone"] = f"{word} 的谐音记忆暂时无法生成。"
        if not result["tenses"]:
            result["tenses"] = f"{word} 的词形变化暂时无法获取。"
        if not result["discrimination"]:
            result["discrimination"] = f"{word} 的辨析内容暂时无法获取。"
        if not result["definition"]:
            result["definition"] = f"The definition for {word} is temporarily unavailable."
        if not result["story"]["english"]:
            result["story"]["english"] = f"A story about {word} is temporarily unavailable."
        if not result["story"]["chinese"]:
            result["story"]["chinese"] = f"关于 {word} 的故事暂时无法获取。"
            
        return result

    def extract_content_from_full_text(self, text, word):
        """从完整文本中提取内容"""
        result = {
            "word": word,
            "origin": {
                "etymology": f"单词 {word} 的词源信息暂时无法获取。",
                "mnemonic": {
                    "associative": f"联想记忆：{word} 的相关联想暂时无法生成。",
                    "homophone": f"谐音记忆：{word} 的谐音记忆暂时无法生成。"
                }
            },
            "tenses": f"v. {word} 的词形变化暂时无法获取。",
            "discrimination": f"单词 {word} 的辨析内容暂时无法获取。",
            "story": {
                "english": f"A story about {word} is temporarily unavailable.",
                "chinese": f"关于 {word} 的故事暂时无法获取。"
            }
        }
        
        try:
            # 尝试从文本中提取任何看起来像内容的部分
            # 这里可以添加更多的启发式规则来提取内容
            pass
        except Exception as e:
            logger.warning(f"从完整文本提取内容时出错: {e}")
        
        return result

    def clean_content(self, content):
        """清理提取的内容，移除多余的转义符和格式化问题"""
        if not content:
            return ""
        
        # 移除多余的转义符
        content = content.replace('\\"', '"')
        content = content.replace('\\\\', '\\')
        
        # 移除多余的换行和空格
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # 移除HTML标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余的标点符号
        content = re.sub(r'[，。！？；：""''（）【】]+$', '', content)
        
        return content

    def clean_duplicated_content(self, text):
        """清理重复的内容，只保留第一次出现的有效内容"""
        # 移除明显的重复内容
        lines = text.split('\n')
        cleaned_lines = []
        seen_content = set()
        
        for line in lines:
            # 跳过空行
            if not line.strip():
                continue
            
            # 检查是否是重复的内容（基于关键字段）
            if any(field in line for field in ['"etymology":', '"associative":', '"homophone":', '"tenses":', '"discrimination":', '"english":', '"chinese":']):
                # 提取字段名和值
                field_match = re.match(r'\s*"([^"]+)":\s*"([^"]*)"', line)
                if field_match:
                    field_name = field_match.group(1)
                    field_value = field_match.group(2)
                    
                    # 如果这个字段已经出现过，跳过
                    if field_name in seen_content:
                        continue
                    else:
                        seen_content.add(field_name)
                        cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def explain(self, word: str) -> Dict[str, any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["deepseek"]},
                    {"role": "user", "content": word},
                ],
                temperature=0.1,  # 进一步降低随机性，提高输出一致性
                max_tokens=3000,  # 增加最大token数，确保内容完整
                top_p=0.9,  # 控制输出的多样性
                frequency_penalty=0.1,  # 减少重复内容
                presence_penalty=0.1,  # 鼓励使用不同的表达
            )
            result = response.choices[0].message.content
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "")
            result = re.sub(r'[\x00-\x1f\x7f]', '', result)
            result = self.clean_invalid_json_escapes(result)
            result = self.try_fix_json_common_errors(result)
            
            # 三层解析策略：标准JSON -> 宽容JSON -> 直接提取
            try:
                data = json.loads(result)
            except Exception:
                try:
                    data = demjson3.decode(result)
                except Exception:
                    try:
                        data = self.extract_ai_content_directly(result, word)
                    except Exception as e:
                        with open('config/ai_failed_json.txt', 'a', encoding='utf-8') as f:
                            f.write(f'word: {word}\n原始内容:\n{response.choices[0].message.content}\n清洗后:\n{result}\n异常:{e}\n---\n')
                        logger.error(f"AI内容提取失败，使用默认结构: {e}")
                        return self.normalize_ai_result(self.create_default_ai_structure(word))
            
            return self.normalize_ai_result(data)
        except Exception as e:
            error_msg = f"Failed to get {self.model}'s AI explanation: {str(e)}"
            logger.error(error_msg)
            return self.normalize_ai_result(self.create_default_ai_structure(word))
