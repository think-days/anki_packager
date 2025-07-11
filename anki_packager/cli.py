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
    cleanup_orphaned_audio,
    reset_all_resources
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
        "--list-cache",
        action="store_true",
        help="List all cached AI results",
    )

    parser.add_argument(
        "--delete-cache",
        dest="delete_cache",
        type=str,
        help="Delete AI cache for a specific word",
    )

    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Delete all AI cache",
    )

    parser.add_argument(
        "--cleanup-cache",
        action="store_true",
        help="Remove orphaned AI cache (cache without corresponding words in vocabulary)",
    )

    parser.add_argument(
        "--cleanup-all",
        action="store_true",
        help="Clean up all orphaned resources (audio and cache)",
    )

    parser.add_argument(
        "--delete-word-completely",
        dest="delete_word_completely",
        type=str,
        help="Completely delete a word and all its resources (vocabulary, audio, cache)",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about vocabulary and resources",
    )

    parser.add_argument(
        "--reset-all",
        action="store_true",
        help="一键重置：清空词汇表、删除所有音频文件、清空所有AI缓存和删除牌组文件",
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

    # 缓存管理命令处理
    elif options.list_cache:
        from anki_packager.cache import ai_cache
        cached_words = ai_cache.get_all_cached_words()
        stats = ai_cache.get_cache_stats()
        if cached_words:
            logger.info(f"AI缓存中共有 {len(cached_words)} 个单词，总大小: {stats['cache_size_kb']} KB:")
            for i, word in enumerate(cached_words, 1):
                print(f"{i:3d}. {word}")
        else:
            logger.info("AI缓存为空")
        exit(0)
        
    elif options.delete_cache:
        from anki_packager.cache import ai_cache
        word = options.delete_cache
        if ai_cache.delete(word):
            logger.info(f"单词 '{word}' 的AI缓存已删除")
        else:
            logger.warning(f"单词 '{word}' 在AI缓存中不存在")
        exit(0)
        
    elif options.clear_cache:
        from anki_packager.cache import ai_cache
        count = ai_cache.clear_all()
        logger.info(f"已删除 {count} 个AI缓存条目")
        exit(0)
        
    elif options.cleanup_cache:
        from anki_packager.utils import cleanup_all_resources
        result = cleanup_all_resources()
        logger.info(f"已清理 {result['orphaned_cache']} 个孤立的AI缓存")
        exit(0)
        
    elif options.delete_word_completely:
        word = options.delete_word_completely
        from anki_packager.utils import remove_word_completely
        result = remove_word_completely(word)
        
        if any(result.values()):
            logger.info(f"单词 '{word}' 已完全删除:")
            if result["vocabulary"]:
                logger.info(f"  - 已从生词本中删除")
            if result["audio"]:
                logger.info(f"  - 已删除音频文件 '{word}.mp3'")
            if result["ai_cache"]:
                logger.info(f"  - 已删除AI缓存")
        else:
            logger.warning(f"单词 '{word}' 不存在或删除失败")
        exit(0)
        
    elif options.cleanup_all:
        from anki_packager.utils import cleanup_all_resources
        result = cleanup_all_resources()
        logger.info(f"资源清理完成:")
        logger.info(f"  - 已删除 {result['orphaned_audio']} 个孤立的音频文件")
        logger.info(f"  - 已删除 {result['orphaned_cache']} 个孤立的AI缓存")
        exit(0)
        
    elif options.stats:
        from anki_packager.utils import get_resources_stats
        stats = get_resources_stats()
        
        print("\n=== 资源统计信息 ===")
        print(f"词汇表单词数量: {stats['vocabulary']['count']}")
        print(f"音频文件数量: {stats['audio']['count']}")
        print(f"孤立音频文件: {stats['audio']['orphaned']['count']}")
        print(f"缺少音频的单词: {stats['audio']['missing']['count']}")
        print(f"AI缓存数量: {stats['ai_cache']['count']} (大小: {stats['ai_cache']['size_kb']} KB)")
        print(f"孤立的AI缓存: {stats['ai_cache']['orphaned']['count']}")
        print(f"缺少AI缓存的单词: {stats['ai_cache']['missing']['count']}")
        
        if stats['audio']['orphaned']['count'] > 0:
            print(f"\n孤立音频文件列表:")
            for word in stats['audio']['orphaned']['words']:
                print(f"  - {word}.mp3")
        
        if stats['audio']['missing']['count'] > 0:
            print(f"\n缺少音频的单词列表:")
            for word in stats['audio']['missing']['words']:
                print(f"  - {word}")
                
        if stats['ai_cache']['orphaned']['count'] > 0:
            print(f"\n孤立的AI缓存列表:")
            for word in stats['ai_cache']['orphaned']['words']:
                print(f"  - {word}")
        
        exit(0)

    elif options.reset_all:
        logger.info("执行一键重置操作...")
        result = reset_all_resources()
        
        logger.info(f"重置结果:")
        if result["vocabulary"]:
            logger.info(f"  - 词汇表已清空")
        else:
            logger.warning(f"  - 词汇表清空失败")
            
        logger.info(f"  - 已删除 {result['audio']} 个音频文件")
        logger.info(f"  - 已清空 {result['ai_cache']} 个AI缓存条目")
        
        if result["deck"]:
            logger.info(f"  - 牌组文件已删除")
        else:
            logger.info(f"  - 牌组文件不存在或删除失败")
            
        logger.info("重置完成！系统已恢复到初始状态")
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
    youdao = YoudaoScraper()

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
        try:
            # 1. 先查词典，判断单词有效性
            youdao_result = None
            try:
                youdao_result = youdao.get_word_info(word)
            except Exception as e:
                logger.warning(f"获取有道词典信息失败: {e}")
            
            # 2. 获取音频
            audio_path = youdao._get_audio(word)
            if not audio_path:
                raise Exception("Failed to get audio")
            audio_files.append(audio_path)
            # 只使用文件名作为 sound 标签的值
            audio_filename = os.path.basename(audio_path)
            data["Pronunciation"] = audio_filename

            # 3. 获取 ECDICT 释义
            dict_def = ecdict.ret_word(word)
            if not dict_def:
                raise Exception("Failed to get ECDICT definition")
            data["ECDict"] = dict_def

            # 4. 获取 AI 释义（如启用）- 仅作为补充
            ai_content = {}
            if ai is not None:
                try:
                    ai_explanation = ai.explain(word)
                    ai_content = ai_explanation or {}
                    
                    # 处理辨析内容 - 词典优先，AI补充
                    if not dict_def.get("diffrentiation") and "discrimination" in ai_content:
                        dict_def["diffrentiation"] = ai_content["discrimination"]
                    
                    # 处理英文释义 - ECDICT过于简单时使用AI的详细释义
                    ecdict_def = dict_def.get("definition", "")
                    if "definition" in ai_content and ai_content["definition"]:
                        ai_def = ai_content["definition"]
                        # 检查ECDICT的释义是否过于简单
                        if not ecdict_def or len(ecdict_def.split()) < 6:
                            dict_def["definition"] = ai_def
                            logger.info(f"使用AI生成的英文释义替换简短的ECDICT释义: {word}")
                        elif len(ecdict_def.split()) < 15:
                            # 如果ECDICT释义不太详细，则合并两者
                            dict_def["definition"] = f"{ecdict_def}; {ai_def}"
                            logger.info(f"合并ECDICT和AI的英文释义: {word}")
                    
                    # 确保AI内容不覆盖词典内容
                    data["AI"] = ai_content
                    
                    # 使用AI生成的短语和例句替代有道爬虫的结果
                    if ai_content and ("phrases" in ai_content or "sentences" in ai_content):
                        # 创建一个有道词典格式的结果对象
                        ai_youdao_result = {
                            "word": word,
                            "example_phrases": [],
                            "example_sentences": []
                        }
                        
                        # 处理短语
                        if "phrases" in ai_content and isinstance(ai_content["phrases"], list):
                            for i, phrase in enumerate(ai_content["phrases"], 1):
                                if isinstance(phrase, dict) and "english" in phrase and "chinese" in phrase:
                                    ai_youdao_result["example_phrases"].append({
                                        "index": str(i),
                                        "english": phrase["english"],
                                        "chinese": phrase["chinese"]
                                    })
                        
                        # 处理例句
                        if "sentences" in ai_content and isinstance(ai_content["sentences"], list):
                            for i, sentence in enumerate(ai_content["sentences"], 1):
                                if isinstance(sentence, dict) and "english" in sentence and "chinese" in sentence:
                                    ai_youdao_result["example_sentences"].append({
                                        "index": str(i),
                                        "english": sentence["english"],
                                        "chinese": sentence["chinese"],
                                        "source": sentence.get("source", "")
                                    })
                        
                        # 优先使用AI生成的内容，如果有有道爬虫结果且AI生成内容为空，则使用有道爬虫结果
                        if ai_youdao_result["example_phrases"] or ai_youdao_result["example_sentences"]:
                            youdao_result = ai_youdao_result
                            logger.info(f"使用AI生成的短语和例句: {word}")
                except Exception as e:
                    logger.warning(f"AI生成内容失败: {e}")
                    data["AI"] = {}
            else:
                data["AI"] = {}
            
            # 如果没有有效的短语和例句数据，创建一个基本结构
            if not youdao_result or (not youdao_result.get("example_phrases") and not youdao_result.get("example_sentences")):
                youdao_result = {
                    "word": word,
                    "example_phrases": [{
                        "index": "1", 
                        "english": word, 
                        "chinese": f"{word}的常用短语暂时无法获取"
                    }],
                    "example_sentences": []
                }
                logger.warning(f"无法获取单词 {word} 的短语和例句，使用占位符")
            
            # 保存最终结果
            data["Youdao"] = youdao_result

            # TODO: Longman English explain

            # 5. 添加到牌组
            anki.add_note(data)
            pbar.update(1)
            pbar.set_description(f"单词 {word} 添加成功")
            return True
        except Exception as e:
            print(f"单词 {word} 不存在或处理失败，已跳过: {e}")
            with open('config/failed.txt', 'a', encoding='utf-8') as f:
                f.write(f"{word}\n")
            return

    retry_words = []
    for word in words:
        try:
            process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
        except Exception as e:
            retry_words.append(word)
            logger.info(f"单词{word}处理出错: {e}，将会重试...")
            continue

    if retry_words:
        logger.info("对处理出错单词进行重试...")
        failed_words = []
        for word in retry_words:
            try:
                process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
            except Exception as e:
                logger.error(f"重试仍然失败... '{word}': {e}")
                failed_words.append(word)

        if failed_words:
            failed_file = os.path.join(config_dir, "failed.txt")
            with open(failed_file, "w") as f:
                for word in failed_words:
                    f.write(f"{word}\n")
            logger.info(f"处理失败的单词已写入: {config_dir}/failed.txt")

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
