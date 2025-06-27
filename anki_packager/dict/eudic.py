import requests
import json
import os
from anki_packager.logger import logger
from anki_packager.utils import get_user_config_dir


# https://my.eudic.net/OpenAPI/doc_api_study#-studylistapi-getcategory


class EUDIC:
    def __init__(self, token: str, id: str):
        self.id = id
        self.token = token
        self.header = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        }
        self.studylist_url = (
            "https://api.frdic.com/api/open/v1/studylist/category?language=en"
        )

        self.words_url = "https://api.frdic.com/api/open/v1/studylist/words/"

    def get_studylist(self):
        response = requests.get(self.studylist_url, headers=self.header)
        self.check_token(response.status_code)

        # show list id
        for book in response.json()["data"]:
            logger.info(f"id: {book['id']}, name: {book['name']}")

        return response.json()

    def auto_set_first_studylist_id(self):
        """自动获取并保存第一个生词本的ID到配置文件"""
        try:
            response = requests.get(self.studylist_url, headers=self.header)
            self.check_token(response.status_code)
            
            data = response.json()["data"]
            if data:
                first_book = data[0]
                first_id = str(first_book['id'])
                first_name = first_book['name']
                
                # 更新配置文件
                config_dir = get_user_config_dir()
                config_file = os.path.join(config_dir, "config.json")
                
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                
                cfg["EUDIC_ID"] = first_id
                
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2, ensure_ascii=False)
                
                logger.info(f"已自动设置欧陆词典ID为: {first_id} ({first_name})")
                return first_id
            else:
                logger.error("未找到任何生词本")
                return None
        except Exception as e:
            logger.error(f"自动设置欧陆词典ID失败: {e}")
            return None

    def get_words(self):
        url = self.words_url + str(self.id) + "?language=en&category_id=0"
        response = requests.get(url, headers=self.header)
        self.check_token(response.status_code)
        return response.json()

    def check_token(self, status_code: int):
        if status_code != 200:
            if status_code == 401:
                msg = "前往 https://my.eudic.net/OpenAPI/Authorization 获取 token 写入配置文件"
                logger.error(msg)
                exit(1)
            else:
                msg = "检查填写的 ID 是否正确"
                logger.error(msg)
                exit(1)
