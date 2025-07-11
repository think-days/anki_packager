import os
import json
import time
from typing import Dict, Optional, Any

from anki_packager.utils import get_user_config_dir
from anki_packager.logger import logger


class AICache:
    """管理AI生成结果的缓存系统"""
    
    def __init__(self):
        self.cache_dir = os.path.join(get_user_config_dir(), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.ai_cache_file = os.path.join(self.cache_dir, "ai_cache.json")
        self.cache_data = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """加载缓存数据"""
        if os.path.exists(self.ai_cache_file):
            try:
                with open(self.ai_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"缓存文件加载失败: {e}")
                return {}
        return {}
    
    def _save_cache(self):
        """保存缓存数据"""
        try:
            with open(self.ai_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"缓存文件保存失败: {e}")
    
    def get(self, word: str) -> Optional[Dict[str, Any]]:
        """获取单词的AI缓存结果"""
        word = word.lower().strip()  # 标准化单词
        if word in self.cache_data:
            cache_entry = self.cache_data[word]
            # 返回缓存内容的深拷贝，避免意外修改
            return json.loads(json.dumps(cache_entry['data']))
        return None
    
    def set(self, word: str, ai_result: Dict[str, Any]):
        """缓存单词的AI结果"""
        word = word.lower().strip()  # 标准化单词
        self.cache_data[word] = {
            'timestamp': int(time.time()),
            'data': ai_result
        }
        self._save_cache()
        
    def delete(self, word: str) -> bool:
        """删除单词的缓存"""
        word = word.lower().strip()  # 标准化单词
        if word in self.cache_data:
            del self.cache_data[word]
            self._save_cache()
            return True
        return False
    
    def delete_multiple(self, words: list) -> int:
        """批量删除多个单词的缓存，返回成功删除的数量"""
        count = 0
        for word in words:
            word = word.lower().strip()
            if word in self.cache_data:
                del self.cache_data[word]
                count += 1
        if count > 0:
            self._save_cache()
        return count
    
    def clear_all(self) -> int:
        """清空所有缓存，返回清除的条目数量"""
        count = len(self.cache_data)
        self.cache_data = {}
        self._save_cache()
        return count
    
    def get_all_cached_words(self) -> list:
        """获取所有已缓存的单词列表"""
        return list(self.cache_data.keys())
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'total_words': len(self.cache_data),
            'cache_size_kb': os.path.getsize(self.ai_cache_file) // 1024 if os.path.exists(self.ai_cache_file) else 0,
            'words': list(self.cache_data.keys())
        }


# 创建全局单例
ai_cache = AICache() 