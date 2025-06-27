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
    """
    return "D:\\Code\\anki_packager"


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
