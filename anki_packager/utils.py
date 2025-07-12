import os
import json
import platform
import shutil

# import requests
# import shutil
# from anki_packager.logger import logger


def get_project_root():
    """
    Returns the project root directory.
    自动检测当前项目根目录，兼容不同操作系统。
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_user_config_dir():
    """
    Returns the project configuration directory.
    """
    return os.path.join(get_project_root(), "config")


def get_dicts_dir():
    """
    Returns the dictionary directory path.
    """
    return os.path.join(get_project_root(), "dicts")


def get_audio_dir():
    """
    Returns the audio directory path.
    """
    return os.path.join(get_project_root(), "audio")


def get_vocabulary_path():
    """
    Returns the vocabulary.txt file path.
    """
    return os.path.join(get_user_config_dir(), "vocabulary.txt")


def read_vocabulary():
    """
    Read vocabulary words from file.
    """
    vocab_path = get_vocabulary_path()
    if not os.path.exists(vocab_path):
        return []
    
    with open(vocab_path, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words


def write_vocabulary(words):
    """
    Write vocabulary words to file.
    """
    vocab_path = get_vocabulary_path()
    with open(vocab_path, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(word + '\n')


def add_word_to_vocabulary(word):
    """
    Add a word to vocabulary if not exists.
    """
    words = read_vocabulary()
    if word not in words:
        words.append(word)
        write_vocabulary(words)
        return True
    return False


def remove_word_from_vocabulary(word):
    """
    Remove a word from vocabulary.
    """
    words = read_vocabulary()
    if word in words:
        words.remove(word)
        write_vocabulary(words)
        return True
    return False


def clear_vocabulary():
    """
    Clear all words from vocabulary.
    """
    write_vocabulary([])


def get_audio_files():
    """
    Get all audio files in audio directory.
    """
    audio_dir = get_audio_dir()
    if not os.path.exists(audio_dir):
        return []
    
    audio_files = []
    for filename in os.listdir(audio_dir):
        if filename.endswith('.mp3'):
            word = filename[:-4]  # Remove .mp3 extension
            audio_files.append(word)
    return audio_files


def delete_audio_file(word):
    """
    Delete audio file for a specific word.
    """
    audio_dir = get_audio_dir()
    audio_file = os.path.join(audio_dir, f"{word}.mp3")
    if os.path.exists(audio_file):
        os.remove(audio_file)
        return True
    return False


def delete_all_audio_files():
    """
    Delete all audio files.
    """
    audio_dir = get_audio_dir()
    if not os.path.exists(audio_dir):
        return 0
    
    count = 0
    for filename in os.listdir(audio_dir):
        if filename.endswith('.mp3'):
            file_path = os.path.join(audio_dir, filename)
            os.remove(file_path)
            count += 1
    return count


def get_orphaned_audio_files():
    """
    Get audio files that don't have corresponding words in vocabulary.
    """
    audio_words = set(get_audio_files())
    vocab_words = set(read_vocabulary())
    return list(audio_words - vocab_words)


def get_missing_audio_files():
    """
    Get words in vocabulary that don't have corresponding audio files.
    """
    audio_words = set(get_audio_files())
    vocab_words = set(read_vocabulary())
    return list(vocab_words - audio_words)


def cleanup_orphaned_audio():
    """
    Remove audio files that don't have corresponding words in vocabulary.
    """
    orphaned = get_orphaned_audio_files()
    count = 0
    for word in orphaned:
        if delete_audio_file(word):
            count += 1
    return count


def get_ai_cache_dir():
    """
    Returns the AI cache directory path.
    """
    cache_dir = os.path.join(get_user_config_dir(), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def initialize_config():
    config_dir = get_user_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    dicts_dir = get_dicts_dir()
    os.makedirs(dicts_dir, exist_ok=True)

    # Default configuration
    default_config = {
        "API_KEY": "",
        "API_BASE": "https://api.siliconflow.cn",
        "MODEL": "Pro/deepseek-ai/DeepSeek-V3",
        "PROXY": "127.0.0.1:63797",
        "EUDIC_TOKEN": "",
        "EUDIC_ID": "0",
        "DECK_NAME": "anki-packager",
    }

    config_path = os.path.join(config_dir, "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

    vocab_path = os.path.join(config_dir, "vocabulary.txt")
    if not os.path.exists(vocab_path):
        with open(vocab_path, "w", encoding="utf-8") as f:
            f.write("")

    failed_path = os.path.join(config_dir, "failed.txt")
    if not os.path.exists(failed_path):
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write("")

    print(f"\033[1;31m配置文件位于 {config_path} \033[0m")


def remove_word_completely(word):
    """
    完全删除一个单词及其相关资源（生词本、音频、AI缓存）。
    返回一个字典，指示每种资源的删除状态。
    """
    result = {
        "vocabulary": False,  # 生词本
        "audio": False,       # 音频文件
        "ai_cache": False,    # AI缓存
    }
    
    # 1. 从生词本删除
    result["vocabulary"] = remove_word_from_vocabulary(word)
    
    # 2. 删除音频文件
    result["audio"] = delete_audio_file(word)
    
    # 3. 删除AI缓存
    # 延迟导入，避免循环引用
    from anki_packager.cache import ai_cache
    result["ai_cache"] = ai_cache.delete(word)
    
    return result

def remove_words_completely(words):
    """
    批量完全删除多个单词及其相关资源。
    返回删除成功的单词数量。
    """
    success_count = 0
    for word in words:
        result = remove_word_completely(word)
        # 只要有任何一种资源删除成功，就计数
        if any(result.values()):
            success_count += 1
    return success_count

def cleanup_all_resources():
    """
    清理所有孤立资源（孤立的音频文件和AI缓存）。
    返回清理的资源统计信息。
    """
    result = {
        "orphaned_audio": 0,
        "orphaned_cache": 0
    }
    
    # 1. 获取生词本单词集合
    vocab_words = set(read_vocabulary())
    
    # 2. 清理孤立的音频文件
    audio_words = set(get_audio_files())
    orphaned_audio = audio_words - vocab_words
    for word in orphaned_audio:
        if delete_audio_file(word):
            result["orphaned_audio"] += 1
            
    # 3. 清理孤立的AI缓存
    from anki_packager.cache import ai_cache
    cached_words = set(ai_cache.get_all_cached_words())
    orphaned_cache = cached_words - vocab_words
    result["orphaned_cache"] = ai_cache.delete_multiple(list(orphaned_cache))
    
    return result

def get_resources_stats():
    """
    获取所有资源的统计信息。
    """
    # 1. 获取生词本信息
    vocab_words = read_vocabulary()
    
    # 2. 获取音频文件信息
    audio_words = get_audio_files()
    orphaned_audio = set(audio_words) - set(vocab_words)
    missing_audio = set(vocab_words) - set(audio_words)
    
    # 3. 获取AI缓存信息
    from anki_packager.cache import ai_cache
    cache_stats = ai_cache.get_cache_stats()
    cached_words = set(cache_stats["words"])
    orphaned_cache = cached_words - set(vocab_words)
    missing_cache = set(vocab_words) - cached_words
    
    return {
        "vocabulary": {
            "count": len(vocab_words),
            "words": vocab_words
        },
        "audio": {
            "count": len(audio_words),
            "orphaned": {
                "count": len(orphaned_audio),
                "words": list(orphaned_audio)
            },
            "missing": {
                "count": len(missing_audio),
                "words": list(missing_audio)
            }
        },
        "ai_cache": {
            "count": cache_stats["total_words"],
            "size_kb": cache_stats["cache_size_kb"],
            "orphaned": {
                "count": len(orphaned_cache),
                "words": list(orphaned_cache)
            },
            "missing": {
                "count": len(missing_cache),
                "words": list(missing_cache)
            }
        }
    }

def reset_all_resources():
    """
    重置所有资源：清空词汇表、删除所有音频文件、清空所有AI缓存和删除生成的牌组文件
    
    Returns:
        dict: 包含各项操作结果的字典
    """
    result = {
        "vocabulary": False,
        "audio": 0,
        "ai_cache": 0,
        "deck": False
    }
    
    # 清空词汇表
    try:
        clear_vocabulary()
        result["vocabulary"] = True
    except Exception as e:
        print(f"清空词汇表失败: {e}")
    
    # 删除所有音频文件
    try:
        audio_count = delete_all_audio_files()
        result["audio"] = audio_count
    except Exception as e:
        print(f"删除音频文件失败: {e}")
    
    # 清空所有AI缓存
    try:
        from anki_packager.cache import ai_cache
        cache_count = ai_cache.clear_all()
        result["ai_cache"] = cache_count
    except Exception as e:
        print(f"清空AI缓存失败: {e}")
    
    # 删除生成的牌组文件
    try:
        import os
        from anki_packager.packager.deck import AnkiDeckCreator
        from anki_packager.logger import logger
        
        # 获取默认牌组名称
        config_dir = get_user_config_dir()
        config_file = os.path.join(config_dir, "config.json")
        deck_name = "anki_packager"
        
        try:
            with open(config_file, "r") as cfg_file:
                import json
                cfg = json.load(cfg_file)
                deck_name = cfg.get("DECK_NAME", "anki_packager")
        except:
            pass
        
        deck_file = f"{deck_name}.apkg"
        if os.path.exists(deck_file):
            os.remove(deck_file)
            result["deck"] = True
    except Exception as e:
        print(f"删除牌组文件失败: {e}")
    
    return result
