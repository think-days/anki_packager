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
    def __init__(self, proxy=None):
        self.base_url = "https://m.youdao.com/result"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.audio_dir = os.path.join(get_project_root(), "audio")
        os.makedirs(self.audio_dir, exist_ok=True)
        self.tmp = tempfile.mkdtemp()
        
        # 设置代理
        self.proxies = None
        if proxy:
            if not proxy.startswith(('http://', 'https://')):
                proxy = f"http://{proxy}"
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
            logger.info(f"有道词典使用代理: {proxy}")

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
                # 为 gTTS 设置代理
                if self.proxies and 'https' in self.proxies:
                    os.environ['HTTPS_PROXY'] = self.proxies['https']
                    os.environ['HTTP_PROXY'] = self.proxies['http']
                
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

            response = requests.get(self.base_url, params=params, headers=self.headers, proxies=self.proxies)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            result = {
                "word": word,
                "example_phrases": [],
                "example_sentences": [],
            }

            # Extract example phrases
            phrase_ul = soup.find_all("ul", class_="")[0]
            if phrase_ul:
                phrase_lis = phrase_ul.find_all("li", class_="mcols-layout")
                for li in phrase_lis:
                    index = (
                        li.find("span", class_="grey").text.strip()
                        if li.find("span", class_="grey")
                        else None
                    )
                    col2_element = li.find("div", class_="col2")
                    point_element = col2_element.find("a", class_="point")
                    sen_phrase_element = col2_element.find("p", class_="sen-phrase")
                    english = None
                    chinese = None
                    if point_element and sen_phrase_element:
                        english = point_element.text.strip()
                        chinese = sen_phrase_element.text.strip()
                    else:
                        content = col2_element.text.strip()
                        parts = re.split(r"([;；])", content)
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

                    result["example_phrases"].append(
                        {
                            "index": index,
                            "english": english,
                            "chinese": chinese,
                        }
                    )

            # Extract example sentences
            sentence_ul = soup.find_all("ul", class_="")[1]
            if sentence_ul:
                sentence_lis = sentence_ul.find_all("li", class_="mcols-layout")
                for li in sentence_lis:
                    index = (
                        li.find("span", class_="grey index").text.strip()
                        if li.find("span", class_="grey index")
                        else None
                    )
                    english_element = li.find("div", class_="sen-eng")
                    chinese_element = li.find("div", class_="sen-ch")
                    source_element = li.find("div", class_="secondary")

                    english = english_element.text.strip() if english_element else None
                    chinese = chinese_element.text.strip() if chinese_element else None
                    source = source_element.text.strip() if source_element else None

                    result["example_sentences"].append(
                        {
                            "index": index,
                            "english": english,
                            "chinese": chinese,
                            "source": source,
                        }
                    )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    scraper = YoudaoScraper()
    result = scraper.get_word_info("variable")
    print(result)
