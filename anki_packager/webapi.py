from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
import uvicorn

from anki_packager.utils import (
    read_vocabulary, write_vocabulary, add_word_to_vocabulary, remove_word_from_vocabulary, clear_vocabulary,
    get_audio_files, delete_audio_file, delete_all_audio_files, get_orphaned_audio_files, get_missing_audio_files, cleanup_orphaned_audio
)
from anki_packager.packager.deck import AnkiDeckCreator
from anki_packager.dict.youdao import YoudaoScraper
from anki_packager.dict.ecdict import Ecdict
from anki_packager.dict.eudic import EUDIC

# 配置
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
VOCAB_PATH = os.path.join(CONFIG_DIR, 'vocabulary.txt')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'audio')
DICT_DIR = os.path.join(os.path.dirname(__file__), '..', 'dicts')
DECK_NAME = 'anki_packager'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 单词管理接口
@app.get("/api/words")
def get_words():
    return {"words": read_vocabulary()}

@app.post("/api/words")
async def add_word(request: Request):
    data = None
    try:
        data = (await request.json()) if hasattr(request, 'json') else None
    except Exception:
        data = None
    word = None
    if data and isinstance(data, dict):
        word = data.get("word")
    if not word:
        # 兼容表单提交
        form = await request.form()
        word = form.get("word")
    if not word:
        raise HTTPException(status_code=422, detail="缺少单词参数")
    if add_word_to_vocabulary(word):
        return {"success": True, "word": word}
    raise HTTPException(status_code=400, detail="单词已存在")

@app.post("/api/words/batch")
def add_batch_words(words: List[str]):
    added = []
    for word in words:
        if add_word_to_vocabulary(word):
            added.append(word)
    return {"success": True, "added": added}

@app.delete("/api/words/{word}")
def delete_word(word: str):
    if remove_word_from_vocabulary(word):
        delete_audio_file(word)
        return {"success": True, "word": word}
    raise HTTPException(status_code=404, detail="单词不存在")

@app.delete("/api/words")
def clear_words():
    clear_vocabulary()
    delete_all_audio_files()
    return {"success": True}

@app.post("/api/words/cleanup-audio")
def cleanup_audio():
    count = cleanup_orphaned_audio()
    return {"success": True, "count": count}

# 卡片生成相关接口（简化版）
@app.post("/api/cards/generate")
def generate_cards():
    # 这里只做示例，实际应根据前端参数调用生成逻辑
    anki = AnkiDeckCreator(DECK_NAME)
    # ... 省略卡片生成逻辑 ...
    # anki.write_to_file(f"{DECK_NAME}.apkg", ...)
    return {"success": True}

@app.get("/api/cards/progress")
def get_progress():
    # 可实现进度查询
    return {"progress": 100}

@app.get("/api/cards/download")
def download_package():
    apkg_path = os.path.join(os.path.dirname(__file__), '..', f'{DECK_NAME}.apkg')
    if os.path.exists(apkg_path):
        return FileResponse(apkg_path, filename=f'{DECK_NAME}.apkg')
    raise HTTPException(status_code=404, detail="未找到卡片包")

# 文件管理接口
@app.get("/api/files")
def get_files():
    files = os.listdir(DICT_DIR)
    return {"files": files}

@app.post("/api/files/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(DICT_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"success": True, "filename": file.filename}

@app.delete("/api/files/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(DICT_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"success": True}
    raise HTTPException(status_code=404, detail="文件不存在")

@app.get("/api/files/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(DICT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="文件不存在")

# 配置管理接口（简化）
@app.get("/api/config")
def get_config():
    config_file = os.path.join(CONFIG_DIR, "config.json")
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="配置文件不存在")

@app.post("/api/config")
def save_config(config: str = Form(...)):
    config_file = os.path.join(CONFIG_DIR, "config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(config)
    return {"success": True}

@app.post("/api/config/test")
def test_config():
    # 可实现配置测试逻辑
    return {"success": True}

# 统计信息接口
@app.get("/api/stats")
def get_stats():
    vocab_words = read_vocabulary()
    audio_words = get_audio_files()
    orphaned = get_orphaned_audio_files()
    missing = get_missing_audio_files()
    return {
        "vocab_count": len(vocab_words),
        "audio_count": len(audio_words),
        "orphaned_count": len(orphaned),
        "missing_count": len(missing),
        "recent_words": vocab_words[-5:] if vocab_words else []
    }

if __name__ == "__main__":
    uvicorn.run("anki_packager.webapi:app", host="0.0.0.0", port=5000, reload=True) 