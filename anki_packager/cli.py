import argparse
import os
from os import environ as env
import json
from tqdm import tqdm
import signal

### config
from anki_packager.utils import (
    get_user_config_dir, 
    read_vocabulary, 
    write_vocabulary, 
    add_word_to_vocabulary, 
    remove_word_from_vocabulary, 
    clear_vocabulary,
    get_audio_files,
    delete_audio_file,
    delete_all_audio_files,
    get_orphaned_audio_files,
    get_missing_audio_files,
    cleanup_orphaned_audio
)

### logger
from anki_packager.logger import logger

### AI
from anki_packager.ai import MODEL_DICT

### Dictionaries
from anki_packager.dict.youdao import YoudaoScraper
from anki_packager.dict.ecdict import Ecdict
from anki_packager.dict.eudic import EUDIC

### Anki
from anki_packager.packager.deck import AnkiDeckCreator


def create_signal_handler(anki, youdao, audio_files, DECK_NAME, pbar):
    def signal_handler(sig, frame):
        pbar.close()
        logger.info("\033[1;31m程序被 <Ctrl-C> 异常中止...\033[0m")
        logger.info("正在写入已处理完毕的卡片...")
        anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
        youdao._clean_temp_dir()
        logger.info("正在退出...")
        exit(0)

    return signal_handler


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--word", dest="word", type=str, help="word to add")

    parser.add_argument(
        "--retry",
        action="store_true",
        help="Retry processing failed words only from config/failed.txt",
    )

    parser.add_argument(
        "--disable_ai",
        dest="disable_ai",
        action="store_true",
        help="Disable AI completions",
    )

    # ./prog --eudicid: run eudic.get_studylist()
    parser.add_argument(
        "--eudicid",
        action="store_true",
        help="Display EUDIC studylist by id",
    )

    parser.add_argument(
        "--auto-eudicid",
        action="store_true",
        help="Auto set first EUDIC studylist ID to config",
    )

    parser.add_argument(
        "--eudic",
        action="store_true",
        help="Use EUDIC book instead of vocabulary.txt",
    )

    parser.add_argument(
        "--siliconflow_key",
        dest="siliconflow_key",
        type=str,
        default="",
        help="SiliconFlow api key",
    )

    # support user-defined txt file: ./prog --txt demo.txt
    parser.add_argument(
        "--txt",
        dest="txt_file",
        type=str,
        help="Use a custom txt file instead of vocabulary.txt",
    )

    parser.add_argument(
        "--model", dest="model", type=str, help="custome AI model"
    )

    parser.add_argument(
        "-p",
        "--proxy",
        dest="proxy",
        type=str,
        default="",
        help="Default proxy like: http://127.0.0.1:7890",
    )

    parser.add_argument(
        "--api_base",
        metavar="API_BASE_URL",
        dest="api_base",
        type=str,
        help="Default base url other than the SiliconFlow's official API address",
    )

    # 单词管理相关命令
    parser.add_argument(
        "--list-words",
        action="store_true",
        help="List all words in vocabulary.txt",
    )

    parser.add_argument(
        "--remove-word",
        dest="remove_word",
        type=str,
        help="Remove a specific word from vocabulary.txt",
    )

    parser.add_argument(
        "--clear-words",
        action="store_true",
        help="Clear all words from vocabulary.txt",
    )

    parser.add_argument(
        "--list-audio",
        action="store_true",
        help="List all audio files",
    )

    parser.add_argument(
        "--delete-audio",
        dest="delete_audio",
        type=str,
        help="Delete audio file for a specific word",
    )

    parser.add_argument(
        "--clear-audio",
        action="store_true",
        help="Delete all audio files",
    )

    parser.add_argument(
        "--cleanup-audio",
        action="store_true",
        help="Remove orphaned audio files (files without corresponding words in vocabulary)",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about vocabulary and audio files",
    )

    options = parser.parse_args()

    ### set config according to config directory or parsed arguments
    config_dir = get_user_config_dir()
    config_file = os.path.join(config_dir, "config.json")

    ## 1. read config.json
    with open(config_file, "r") as ai_cfg:
        cfg = json.load(ai_cfg)
        API_KEY = cfg["API_KEY"]
        PROXY = cfg["PROXY"]
        API_BASE = cfg["API_BASE"]
        MODEL = cfg["MODEL"]
        EUDIC_TOKEN = cfg["EUDIC_TOKEN"]
        EUDIC_ID = cfg["EUDIC_ID"]
        DECK_NAME = cfg["DECK_NAME"]
    ai_cfg.close()
    logger.info("配置读取完毕")
    logger.info(f"配置文件路径: {config_file}")

    # 单词管理命令处理
    if options.list_words:
        words = read_vocabulary()
        if words:
            logger.info(f"词汇表中共有 {len(words)} 个单词:")
            for i, word in enumerate(words, 1):
                print(f"{i:3d}. {word}")
        else:
            logger.info("词汇表为空")
        exit(0)

    elif options.remove_word:
        word = options.remove_word
        if remove_word_from_vocabulary(word):
            logger.info(f"单词 '{word}' 已从词汇表中删除")
            # 同时删除对应的音频文件
            if delete_audio_file(word):
                logger.info(f"音频文件 '{word}.mp3' 已删除")
        else:
            logger.warning(f"单词 '{word}' 不在词汇表中")
        exit(0)

    elif options.clear_words:
        clear_vocabulary()
        logger.info("词汇表已清空")
        exit(0)

    elif options.list_audio:
        audio_files = get_audio_files()
        if audio_files:
            logger.info(f"音频目录中共有 {len(audio_files)} 个音频文件:")
            for i, word in enumerate(audio_files, 1):
                print(f"{i:3d}. {word}.mp3")
        else:
            logger.info("音频目录为空")
        exit(0)

    elif options.delete_audio:
        word = options.delete_audio
        if delete_audio_file(word):
            logger.info(f"音频文件 '{word}.mp3' 已删除")
        else:
            logger.warning(f"音频文件 '{word}.mp3' 不存在")
        exit(0)

    elif options.clear_audio:
        count = delete_all_audio_files()
        logger.info(f"已删除 {count} 个音频文件")
        exit(0)

    elif options.cleanup_audio:
        orphaned = get_orphaned_audio_files()
        if orphaned:
            logger.info(f"发现 {len(orphaned)} 个孤立音频文件:")
            for word in orphaned:
                print(f"  - {word}.mp3")
            
            count = cleanup_orphaned_audio()
            logger.info(f"已清理 {count} 个孤立音频文件")
        else:
            logger.info("没有发现孤立的音频文件")
        exit(0)

    elif options.stats:
        vocab_words = read_vocabulary()
        audio_words = get_audio_files()
        orphaned = get_orphaned_audio_files()
        missing = get_missing_audio_files()
        
        print("\n=== 词汇和音频文件统计 ===")
        print(f"词汇表单词数量: {len(vocab_words)}")
        print(f"音频文件数量: {len(audio_words)}")
        print(f"孤立音频文件: {len(orphaned)}")
        print(f"缺少音频的单词: {len(missing)}")
        
        if orphaned:
            print(f"\n孤立音频文件列表:")
            for word in orphaned:
                print(f"  - {word}.mp3")
        
        if missing:
            print(f"\n缺少音频的单词列表:")
            for word in missing:
                print(f"  - {word}")
        
        exit(0)

    # display eudict id only
    if options.eudicid:
        logger.info("设置：仅读取欧路词典 ID")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic.get_studylist()
        exit(0)

    # auto set first eudic studylist id
    elif options.auto_eudicid:
        logger.info("设置：自动设置第一个欧路词典生词本ID")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        new_id = eudic.auto_set_first_studylist_id()
        if new_id:
            logger.info("欧路词典ID设置成功，现在可以直接使用 --eudic 参数")
        exit(0)

    # only add word into vocabulary.txt line by line
    elif options.word:
        WORD = options.word
        if add_word_to_vocabulary(WORD):
            logger.info(f"单词: {WORD} 已添加进词汇表")
        else:
            logger.info(f"单词: {WORD} 已存在于词汇表中")
        exit(0)

    words = []
    retry_words = []
    number_words = 0
    audio_files = []
    ai = None

    anki = AnkiDeckCreator(f"{DECK_NAME}")
    ecdict = Ecdict()
    
    # 获取代理设置
    current_proxy = options.proxy or PROXY
    
    # 初始化 YoudaoScraper 并传递代理参数
    youdao = YoudaoScraper(proxy=current_proxy)

    # AI 配置
    if options.disable_ai:
        logger.info("AI 功能已关闭")
    else:
        PROXY = options.proxy or PROXY
        if PROXY:
            env["HTTP_PROXY"] = PROXY
            env["HTTPS_PROXY"] = PROXY
            logger.info(f"使用代理: {PROXY}")

        API_BASE = options.api_base or API_BASE
        MODEL = options.model or MODEL
        if not MODEL:
            logger.error("未设置 AI 模型，请在配置文件或使用 --model 参数指定")
            exit(1)

        # 检查模型是否在支持列表中
        if MODEL not in MODEL_DICT:
            logger.error(f"目前只支持的模型有：{', '.join(MODEL_DICT.keys())}")
            exit(1)

        # 根据模型类型设置对应的 API 密钥
        model_class = MODEL_DICT[MODEL].__module__.split(".")[-1]
        if model_class == "siliconflow":
            API_KEY = options.siliconflow_key or env.get("SILICONFLOW_API_KEY") or API_KEY
        elif model_class == "openrouter":
            # 对于OpenRouter，使用OPENROUTER_API_KEY和OPENROUTER_API_BASE
            API_KEY = env.get("OPENROUTER_API_KEY") or cfg.get("OPENROUTER_API_KEY", "")
            API_BASE = cfg.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

        if not API_KEY:
            logger.error(f"缺少{model_class} API 密钥")
            exit(1)

        # 5. 初始化 AI 模型
        try:
            if model_class == "openrouter":
                ai = MODEL_DICT[MODEL](API_KEY, API_BASE, MODEL)
            else:
                ai = MODEL_DICT[MODEL](MODEL, API_KEY, API_BASE)
            logger.info(f"当前使用的 AI 模型: {MODEL}")
        except Exception as e:
            logger.error(f"初始化 AI 模型失败: {e}")
            exit(1)
    ## 4. vocabulary source: eudic data, custom txt file, or default vocabulary.txt
    if options.eudic:
        logger.info("配置: 对欧路词典生词本单词进行处理...")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic_words = eudic.get_words()["data"]
        for word in eudic_words:
            words.append(word["word"])
        number_words = len(words)
    elif options.txt_file:
        txt_file_path = options.txt_file
        if not os.path.isabs(txt_file_path):
            # If relative path, resolve from current directory
            txt_file_path = os.path.abspath(txt_file_path)

        logger.info(f"配置: 对自定义单词文件 {txt_file_path} 进行处理...")
        try:
            with open(txt_file_path, "r") as vocab:
                for word in vocab:
                    word = word.strip()
                    if word:  # Skip empty lines
                        words.append(word)
                number_words = len(words)
        except FileNotFoundError:
            logger.error(f"文件 {txt_file_path} 未找到")
            exit(1)
        except Exception as e:
            logger.error(f"读取文件 {txt_file_path} 出错: {e}")
            exit(1)
    else:
        vocab_path = os.path.join(config_dir, "vocabulary.txt")
        logger.info(f"配置: 对默认生词本单词 {vocab_path} 进行处理...")
        try:
            with open(vocab_path, "r") as vocab:
                for word in vocab:
                    word = word.strip()
                    if word:  # Skip empty lines
                        words.append(word)
                number_words = len(words)
            logger.info(f"从默认词库读取了 {number_words} 个单词")
        except FileNotFoundError:
            logger.error(f"默认词库文件 {vocab_path} 未找到")
            exit(1)
        except Exception as e:
            logger.error(f"读取默认词库文件出错: {e}")
            exit(1)
        vocab.close()

    pbar = tqdm(total=number_words, desc="开始处理")
    signal.signal(
        signal.SIGINT,
        create_signal_handler(anki, youdao, audio_files, DECK_NAME, pbar),
    )

    def process_word(word, ai, anki, youdao, ecdict, audio_files, pbar):
        data = {}
        data["Word"] = word
        audio_path = None
        
        try:
            # 1. 首先检查单词是否存在于词典中
            dict_def = ecdict.ret_word(word)
            if not dict_def:
                raise Exception("Failed to get ECDICT definition")
            data["ECDict"] = dict_def

            # 2. 获取有道词典信息
            youdao_result = youdao.get_word_info(word)
            if not youdao_result:
                raise Exception("Failed to get Youdao information")
            data["Youdao"] = youdao_result

            # 3. 生成音频文件（只有在前面步骤都成功后才生成）
            audio_path = youdao._get_audio(word)
            if not audio_path:
                raise Exception("Failed to get audio")

            audio_files.append(audio_path)
            # 只使用文件名作为 sound 标签的值
            audio_filename = os.path.basename(audio_path)
            data["Pronunciation"] = audio_filename

            # 4. 获取AI解释（如果启用）
            if ai is not None:
                ai_explanation = ai.explain(word)
                data["AI"] = ai_explanation
            else:
                data["AI"] = {}

            # 5. 辨析字段AI补全
            if not data["ECDict"].get("diffrentiation") and ai is not None:
                try:
                    ai_explanation = ai.explain(word)
                    if ai_explanation and "discrimination" in ai_explanation:
                        data["ECDict"]["diffrentiation"] = ai_explanation["discrimination"]
                except Exception as e:
                    logger.warning(f"AI补全辨析内容失败: {e}")

            # 6. 添加笔记到牌组
            anki.add_note(data)
            pbar.update(1)
            pbar.set_description(f"单词 {word} 添加成功")
            return True
            
        except Exception as e:
            # 如果处理失败，清理已创建的音频文件
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                    logger.info(f"清理失败的音频文件: {audio_path}")
                except Exception as cleanup_error:
                    logger.warning(f"清理音频文件失败: {cleanup_error}")
            
            logger.error(f"单词 {word} 处理失败: {e}")
            with open('config/failed.txt', 'a', encoding='utf-8') as f:
                f.write(f"{word}\n")
            return False

    retry_words = []
    for word in words:
        success = process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
        if not success:
            retry_words.append(word)

    if retry_words:
        logger.info(f"对 {len(retry_words)} 个处理出错的单词进行重试...")
        failed_words = []
        for word in retry_words:
            logger.info(f"重试处理单词: {word}")
            success = process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
            if not success:
                failed_words.append(word)
                logger.error(f"重试仍然失败: {word}")

        if failed_words:
            failed_file = os.path.join(config_dir, "failed.txt")
            with open(failed_file, "w", encoding='utf-8') as f:
                for word in failed_words:
                    f.write(f"{word}\n")
            logger.info(f"处理失败的单词已写入: {failed_file}")
            logger.info(f"最终失败单词数量: {len(failed_words)}")

    # 关闭 pbar 避免多输出一次
    pbar.close()
    try:
        if anki.added:
            anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
            logger.info(f"牌组生成完毕，请打开 {DECK_NAME}.apkg")
    except Exception as e:
        logger.error(f"Error saving Anki deck: {e}")
    try:
        youdao._clean_temp_dir()
    except Exception as e:
        logger.error(f"Error cleaning up audio files: {e}")


if __name__ == "__main__":
    main()
