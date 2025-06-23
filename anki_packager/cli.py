import argparse
import os
import json
from tqdm import tqdm

from anki_packager.logger import logger
from anki_packager.dict.ecdict import Ecdict
from anki_packager.dict.youdao import YoudaoScraper
from anki_packager.packager.deck import AnkiDeckCreator
from anki_packager.ai.siliconflow import SiliconFlow

# 永远只用本项目根目录下的 config/ 目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
VOCAB_PATH = os.path.join(CONFIG_DIR, "vocabulary.txt")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def ai_to_str(ai_data):
    if not ai_data or not isinstance(ai_data, dict):
        return ""
    origin = ai_data.get("origin", {})
    tenses = ai_data.get("tenses", "")
    etymology = origin.get("etymology", "")
    associative = origin.get("mnemonic", {}).get("associative", "")
    homophone = origin.get("mnemonic", {}).get("homophone", "")
    lines = []
    if etymology:
        lines.append(f"【词源】{etymology}")
    if associative or homophone:
        lines.append(f"【助记】{associative}；{homophone}")
    if tenses:
        lines.append(f"【词形变化】{tenses}")
    return "<br>".join(lines)

def story_to_str(ai_data):
    if not ai_data or not isinstance(ai_data, dict):
        return ""
    story = ai_data.get("story", {})
    english = story.get("english", "")
    chinese = story.get("chinese", "")
    if english or chinese:
        return f"{english}<br>{chinese}"
    return ""

def yd_to_str(yd_data):
    if not yd_data:
        return ""
    if isinstance(yd_data, str):
        try:
            yd = json.loads(yd_data)
        except Exception:
            return yd_data
    else:
        yd = yd_data

    output = []
    if yd.get("example_phrases"):
        output.append("【短语】")
        for item in yd["example_phrases"]:
            en = item.get("english", "")
            zh = item.get("chinese", "")
            output.append(f"<li><b>{en}</b> {zh}</li>")
    if yd.get("example_sentences"):
        output.append("【例句】")
        for item in yd["example_sentences"]:
            en = item.get("english", "")
            zh = item.get("chinese", "")
            output.append(f"<li><b>{en}</b> {zh}</li>")
    return "<br>".join(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--word", type=str, help="Add a word to vocabulary")
    parser.add_argument("--disable_ai", action="store_true", help="Disable AI completions")
    parser.add_argument("--txt", type=str, help="Custom vocabulary file")
    options = parser.parse_args()

    # 配置只读本地 config/
    with open(CONFIG_PATH, "r", encoding="utf-8") as ai_cfg:
        cfg = json.load(ai_cfg)
    API_KEY = cfg["API_KEY"]
    API_BASE = cfg["API_BASE"]
    MODEL = cfg["MODEL"]
    DECK_NAME = cfg.get("DECK_NAME", "apkger")
    DECK_PATH = os.path.join(PROJECT_ROOT, f"{DECK_NAME}.apkg")

    if options.word:
        vocab_path = VOCAB_PATH
        with open(vocab_path, "a", encoding="utf-8") as f:
            f.write(options.word + "\n")
        logger.info(f"单词: {options.word} 已添加进 {vocab_path}")
        exit(0)

    words = []
    vocab_path = options.txt if options.txt else VOCAB_PATH
    print("读取词表路径:", vocab_path)
    with open(vocab_path, "r", encoding="utf-8") as vocab:
        for word in vocab:
            word = word.strip()
            if word:
                words.append(word)
    logger.info(f"将处理 {len(words)} 个单词。")
    print("words:", words)

    anki = AnkiDeckCreator(DECK_NAME)
    ecdict = Ecdict()
    youdao = YoudaoScraper()
    ai = None if options.disable_ai else SiliconFlow(MODEL, API_KEY, API_BASE)
    audio_files = []
    pbar = tqdm(total=len(words), desc="生成中")

    for word in words:
        try:
            ec_data = ecdict.ret_word(word)
            yd_data = youdao.get_word_info(word)
            ai_data = ai.explain(word) if ai else {}

            note_data = {
                "Word": str(word),
                "Pronunciation": str(ec_data.get("phonetic", "")),
                "Front": str(ec_data.get("phonetic", "")),
                "ECDict": str(ec_data.get("translation", "")),
                "Longman": "",
                "Youdao": yd_to_str(yd_data),
                "AI": ai_to_str(ai_data),
                "Discrimination": str(ec_data.get("diffrentiation", "")),
                "Story": story_to_str(ai_data),
            }
            anki.add_note(note_data)
        except Exception as e:
            logger.error(f"处理单词 {word} 时出错: {e}")
        pbar.update(1)

    anki.write_to_file(DECK_PATH, audio_files)
    logger.info(f"Anki卡片包已生成到: {DECK_PATH}")
    pbar.close()
