import os
import re
import shutil
import tempfile
import requests
import edge_tts
import asyncio
from gtts import gTTS
from bs4 import BeautifulSoup
from typing import Dict, Optional
from anki_packager.logger import logger
from anki_packager.utils import get_project_root


class YoudaoScraper:
    def __init__(self):
        self.base_url = "https://m.youdao.com/result"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.audio_dir = os.path.join(get_project_root(), "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        self.tmp = tempfile.mkdtemp()

    async def generate_edge_tts(self, word, filename):
        communicate = edge_tts.Communicate(word, voice="en-GB-RyanNeural")
        await communicate.save(filename)

    def _get_audio(self, word: str):
        """优先复用audio目录下的音频文件，否则生成"""
        filename = os.path.join(self.audio_dir, f"{word}.mp3")
        if os.path.exists(filename):
            logger.info(f"音频文件已存在，跳过生成: {word}.mp3")
            return filename
        
        logger.info(f"开始生成音频文件: {word}.mp3")
        try:
            asyncio.run(self.generate_edge_tts(word, filename))
            logger.info(f"音频文件生成成功: {word}.mp3")
        except Exception as e:
            logger.warning(f"Edge TTS生成失败，使用gTTS备用方案: {e}")
            try:
                tts = gTTS(text=word, lang="en")
                tts.save(filename)
                logger.info(f"gTTS音频文件生成成功: {word}.mp3")
            except Exception as e2:
                logger.error(f"音频文件生成失败: {word}.mp3 - {e2}")
                return None
        return filename

    def _clean_temp_dir(self):
        """只清理临时目录，不清理audio目录"""
        try:
            if os.path.exists(self.tmp):
                shutil.rmtree(self.tmp)
                logger.debug(f"音频临时文件夹已清理: {self.tmp}")
        except Exception as e:
            logger.error(f"音频临时文件夹 {self.tmp} 清理失败: {e}")

    def get_word_info(self, word: str) -> Optional[Dict]:
        try:
            params = {"word": word, "lang": "en"}

            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            result = {
                "word": word,
                "example_phrases": [],
                "example_sentences": [],
            }

            # 尝试专用处理，针对有道词典新版UI结构
            try:
                # 1. 从新版UI中提取短语
                # 首先尝试获取更具体的容器
                phrase_containers = soup.find_all("div", class_="word-exp")
                if phrase_containers:
                    for container in phrase_containers:
                        # 移除所有与音频播放相关的元素
                        for elem in container.find_all(["span", "div"], class_=["voice", "role", "pronounce", "sound"]):
                            elem.decompose()
                        
                        # 移除语速控制等元素
                        for elem in container.find_all(text=re.compile(r'(0\.\d+x|1\.\d+X|发音|英式|美式)')):
                            if elem.parent:
                                elem.parent.decompose()
                        
                        # 提取短语
                        phrases = container.find_all("li", class_="mcols-layout")
                        for li in phrases:
                            # 清理li内部可能存在的播放控件
                            for elem in li.find_all(["span", "div"], class_=["voice", "role", "pronounce", "sound"]):
                                elem.decompose()
                            
                            # 提取索引、英文和中文
                            index_elem = li.find("span", class_="grey")
                            index = index_elem.text.strip() if index_elem else "1"
                            
                            col2 = li.find("div", class_="col2")
                            if col2:
                                # 清理掉所有播放控件和不必要的元素
                                for elem in col2.find_all(["span", "div", "a"], class_=["voice", "pronounce", "sound"]):
                                    elem.decompose()
                                
                                # 提取英文部分
                                point_elem = col2.find("a", class_="point")
                                english = ""
                                if point_elem:
                                    english = point_elem.text.strip()
                                
                                # 提取中文部分
                                cn_elem = col2.find("p", class_="sen-phrase")
                                chinese = ""
                                if cn_elem:
                                    chinese = cn_elem.text.strip()
                                
                                # 如果上面的尝试没有提取到内容，直接使用文本
                                if not english and not chinese:
                                    content = col2.text.strip()
                                    # 清理内容中的UI元素文本
                                    content = re.sub(r'(0\.\d+x|1\.\d+X|发音|英式|美式|语速)', '', content)
                                    content = re.sub(r'\s+', ' ', content).strip()
                                    
                                    # 尝试分离英文和中文
                                    parts = re.split(r'([;；])', content)
                                    parts = [s.strip() for s in parts if s.strip() and s not in [";", "；"]]
                                    
                                    if len(parts) > 1:
                                        english = parts[0]
                                        chinese = "".join(parts[1:])
                                    else:
                                        english = content
                                
                                # 最终清理
                                english = self._clean_text(english)
                                chinese = self._clean_text(chinese)
                                
                                # 只有当英文和中文不为空时才添加
                                if english or chinese:
                                    result["example_phrases"].append({
                                        "index": index,
                                        "english": english,
                                        "chinese": chinese
                                    })
                
                # 2. 提取例句
                sentence_containers = soup.find_all("ul", class_="")
                if len(sentence_containers) > 1:
                    sentence_container = sentence_containers[1]
                    sentences = sentence_container.find_all("li", class_="mcols-layout")
                    
                    for li in sentences:
                        # 清理播放控件
                        for elem in li.find_all(["span", "div"], class_=["voice", "pronounce", "sound"]):
                            elem.decompose()
                        
                        # 提取索引
                        index_elem = li.find("span", class_="grey index")
                        index = index_elem.text.strip() if index_elem else "1"
                        
                        # 提取英文例句
                        eng_elem = li.find("div", class_="sen-eng")
                        english = ""
                        if eng_elem:
                            english = eng_elem.text.strip()
                        
                        # 提取中文翻译
                        ch_elem = li.find("div", class_="sen-ch")
                        chinese = ""
                        if ch_elem:
                            chinese = ch_elem.text.strip()
                        
                        # 提取来源
                        source_elem = li.find("div", class_="secondary")
                        source = ""
                        if source_elem:
                            source = source_elem.text.strip()
                        
                        # 清理文本
                        english = self._clean_text(english)
                        chinese = self._clean_text(chinese)
                        source = self._clean_text(source)
                        
                        # 只有当英文和中文不为空时才添加
                        if english or chinese:
                            result["example_sentences"].append({
                                "index": index,
                                "english": english,
                                "chinese": chinese,
                                "source": source
                            })
            except Exception as e:
                logger.warning(f"新版UI解析失败，尝试备用方案: {e}")
            
            # 如果上面的尝试没有提取到任何内容，使用通用提取方式
            if not result["example_phrases"] and not result["example_sentences"]:
                # Extract example phrases
                phrase_uls = soup.find_all("ul", class_="")
                if phrase_uls and len(phrase_uls) > 0:  # 确保找到了ul元素
                    phrase_ul = phrase_uls[0]
                    phrase_lis = phrase_ul.find_all("li", class_="mcols-layout")
                    for li in phrase_lis:
                        try:
                            # 清理播放控件
                            for elem in li.find_all(["span", "div"], class_=["voice", "pronounce", "sound"]):
                                elem.decompose()
                            
                            index = (
                                li.find("span", class_="grey").text.strip()
                                if li.find("span", class_="grey")
                                else "1"
                            )
                            col2_element = li.find("div", class_="col2")
                            if not col2_element:  # 跳过不符合预期的元素
                                continue
                            
                            # 清理col2中的播放控件
                            for elem in col2_element.find_all(["span", "div"], class_=["voice", "pronounce", "sound"]):
                                elem.decompose()
                            
                            point_element = col2_element.find("a", class_="point")
                            sen_phrase_element = col2_element.find("p", class_="sen-phrase")
                            english = None
                            chinese = None
                            if point_element and sen_phrase_element:
                                english = point_element.text.strip()
                                chinese = sen_phrase_element.text.strip()
                            else:
                                content = col2_element.text.strip()
                                # 清理内容中的UI元素文本
                                content = re.sub(r'(0\.\d+x|1\.\d+X|发音|英式|美式|语速)', '', content)
                                content = re.sub(r'\s+', ' ', content).strip()
                                
                                parts = re.split(r'([;；])', content)
                                parts = [
                                    s.strip()
                                    for s in parts
                                    if s.strip() and s not in [";", "；"]
                                ]
                                if len(parts) > 1:
                                    english = parts[0]
                                    chinese = "".join(parts[1:])
                                else:
                                    english = content

                            # 最终清理
                            english = self._clean_text(english) if english else ""
                            chinese = self._clean_text(chinese) if chinese else ""
                            
                            # 只有当英文和中文不为空时才添加
                            if english or chinese:
                                result["example_phrases"].append(
                                    {
                                        "index": index,
                                        "english": english,
                                        "chinese": chinese,
                                    }
                                )
                        except Exception as e:
                            logger.warning(f"解析短语出错: {e}")
                            continue  # 继续处理下一个元素

                # Extract example sentences
                if phrase_uls and len(phrase_uls) > 1:  # 确保找到了第二个ul元素
                    sentence_ul = phrase_uls[1]
                    sentence_lis = sentence_ul.find_all("li", class_="mcols-layout")
                    for li in sentence_lis:
                        try:
                            # 清理播放控件
                            for elem in li.find_all(["span", "div"], class_=["voice", "pronounce", "sound"]):
                                elem.decompose()
                            
                            index = (
                                li.find("span", class_="grey index").text.strip()
                                if li.find("span", class_="grey index")
                                else "1"
                            )
                            english_element = li.find("div", class_="sen-eng")
                            chinese_element = li.find("div", class_="sen-ch")
                            source_element = li.find("div", class_="secondary")

                            english = english_element.text.strip() if english_element else None
                            chinese = chinese_element.text.strip() if chinese_element else None
                            source = source_element.text.strip() if source_element else None

                            # 最终清理
                            english = self._clean_text(english) if english else ""
                            chinese = self._clean_text(chinese) if chinese else ""
                            source = self._clean_text(source) if source else ""
                            
                            # 只有当英文和中文不为空时才添加
                            if english or chinese:
                                result["example_sentences"].append(
                                    {
                                        "index": index,
                                        "english": english,
                                        "chinese": chinese,
                                        "source": source,
                                    }
                                )
                        except Exception as e:
                            logger.warning(f"解析例句出错: {e}")
                            continue  # 继续处理下一个元素

            # 尝试从页面提取更多内容
            if not result["example_phrases"] and not result["example_sentences"]:
                # 尝试从其他部分提取内容
                basic_containers = soup.find_all("div", class_="trans-container")
                for container in basic_containers:
                    content = container.text.strip()
                    # 移除播放控件相关文本
                    content = re.sub(r'(0\.\d+x|1\.\d+X|发音|英式|美式|语速)', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    # 添加为基本短语
                    if content:
                        result["example_phrases"].append({
                            "index": "1",
                            "english": word,
                            "chinese": self._clean_text(content),
                        })
                        break
            
            # 如果仍然没有内容，添加一个占位符
            if not result["example_phrases"] and not result["example_sentences"]:
                result["example_phrases"].append({
                    "index": "1",
                    "english": word,
                    "chinese": f"找不到{word}的释义",
                })
            
            # 最后的检查：确保没有UI文本残留
            for category in ['example_phrases', 'example_sentences']:
                for i, item in enumerate(result[category]):
                    if 'english' in item:
                        result[category][i]['english'] = self._clean_text(item['english'])
                    if 'chinese' in item:
                        result[category][i]['chinese'] = self._clean_text(item['chinese'])
            
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            # 记录HTML以便调试
            try:
                with open(f"debug_{word}_error.html", "w", encoding="utf-8") as f:
                    f.write(response.text if 'response' in locals() else "No response")
            except Exception:
                pass
            return None

    def _clean_text(self, text):
        """清理文本，移除UI控件文本和多余空格"""
        if not text:
            return ""
        
        # 移除语速控制、发音类型等UI文本
        text = re.sub(r'(0\.\d+x|1\.\d+X|语速|发音|英式|美式|英|美|/.*?/)', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除可能的空括号
        text = re.sub(r'\(\s*\)', '', text)
        
        # 移除前后空白
        text = text.strip()
        
        return text


if __name__ == "__main__":
    scraper = YoudaoScraper()
    result = scraper.get_word_info("variable")
    print(result)
