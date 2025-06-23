import os
import sqlite3
from anki_packager.logger import logger
from anki_packager.utils import get_user_config_dir
from anki_packager.dict import stardict  # 保证dict/stardict.py存在且正确

class Ecdict:
    def __init__(self):
        self.config_dir = get_user_config_dir()
        self.dicts_dir = os.path.join(self.config_dir, "dicts")
        self.sqlite = os.path.join(self.dicts_dir, "stardict.db")
        try:
            self.conn = sqlite3.connect(self.sqlite)
            self.cursor = self.conn.cursor()
            self.sd = stardict.StarDict(self.sqlite, False)
        except Exception as e:
            logger.error(f"Ecdict 初始化失败: {e}")

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass

    def ret_word(self, word: str) -> dict:
        """Return ECDICT data，仅用英式音标释义"""
        data = self.sd.query(word)
        if not data:
            logger.warning(f"查无单词：{word}")
            return {}
        # 只用 phonetic 字段（英式），你需要保证字典数据格式
        data['phonetic'] = data.get('phonetic', '')
        data['definition'] = data.get('definition', '')
        data['translation'] = data.get('translation', '')
        data['diffrentiation'] = data.get('diffrentiation', '')
        return data
