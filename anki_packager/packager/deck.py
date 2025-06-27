import genanki
import random
import re
import html

POS_LIST = ["n.", "v.", "adj.", "adv.", "vt.", "vi."]
ALLOWED_TAGS = ['span', 'div', 'br', 'hr', 'em', 'b', 'i', 'u']

def clean_html(text):
    text = re.sub(r'class="[^"]*"', '', text)
    text = re.sub(r'<[^>]+>\s*</[^>]+>', '', text)
    text = text.replace('\1', '').replace('', '').replace('\\1', '')
    return text

def clean_stats(text):
    text = re.sub(r'词性：[^\n]+', '', text)
    return text

def clean_discrimination(text):
    text = text.replace('|', '；')
    text = re.sub(r'[；|]+$', '', text)
    return text

def clean_associative(text):
    text = re.sub(r'谐音[：:][^\n]+', '', text)
    return text

def clean_placeholder(text):
    if not isinstance(text, str):
        return ""
    text = text.replace('\1', '').replace('\x01', '').replace('\\1', '')
    text = text.strip()
    return text

def highlight_pos(text):
    # 用正则将 n. v. adj. vt. vi. 等词性标记替换为高亮斜体红色
    return re.sub(r'\b(n|v|adj|adv|vt|vi)\.\b', r'<span class="pos-n">\1.</span>', text)

def format_definition(text):
    text = highlight_pos(text)
    lines = re.split(r'[；;。\n]', text)
    return '<br>'.join(line.strip() for line in lines if line.strip())

def highlight_story_en(text, word):
    # 只对目标单词加粗高亮
    return re.sub(f'(?i)({re.escape(word)})', r'<span class="story-highlight">\1</span>', text)

def highlight_story_cn(text, word_cn):
    # 只对目标单词的中文翻译加粗高亮
    if word_cn:
        return text.replace(word_cn, f'<span class="story-cn-highlight">{word_cn}</span>')
    return text

def format_discrimination_field(discrimination):
    # 如果是字符串，直接返回
    if isinstance(discrimination, str):
        return discrimination
    # 如果是dict，格式化为"【title】content"
    elif isinstance(discrimination, dict):
        title = discrimination.get('title', '')
        content = discrimination.get('content', '')
        return f"【{title}】{content}" if title else content
    # 如果是list，递归格式化每一项
    elif isinstance(discrimination, list):
        return '\n'.join([format_discrimination_field(item) for item in discrimination])
    else:
        return str(discrimination) if discrimination else ""

def ensure_str(obj):
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        return str({k: ensure_str(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return ', '.join([ensure_str(x) for x in obj])
    elif obj is None:
        return ""
    else:
        return str(obj)

def escape_invalid_html(text):
    def replacer(match):
        tag = match.group(2)
        if tag.lower() in ALLOWED_TAGS:
            return match.group(0)
        return html.escape(match.group(0))
    return re.sub(r'<(/?)(\w+)[^>]*>', lambda m: replacer(m), text)

def format_tenses_field(tenses):
    # 统一词形变化说明格式
    if not tenses or tenses in ["", None]:
        return "v. 无动词形式"
    if isinstance(tenses, str):
        tenses = tenses.strip()
        if tenses == "无" or tenses.lower() in ["none", "no form", "no forms"]:
            return "v. 无动词形式"
        if tenses.startswith("n.") or tenses.startswith("v.") or tenses.startswith("adj.") or tenses.startswith("adv."):
            return tenses
        if "," in tenses:
            return f"v. {tenses}"
        return tenses
    if isinstance(tenses, (list, tuple)):
        return ", ".join([format_tenses_field(x) for x in tenses])
    return str(tenses)

def wrap_ai_italic(text):
    return f'<span class="ai-italic">{text}</span>' if text else ""

class AnkiDeckCreator:
    def __init__(self, deck_name: str):
        self.added = False
        self.deck_name = deck_name
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = genanki.Model(
            self.model_id,
            "Anki Packager",
            fields=[
                {"name": "Word"},
                {"name": "Pronunciation"},
                {"name": "Front"},
                {"name": "ECDict"},
                {"name": "Longman"},
                {"name": "Youdao"},
                {"name": "AI"},
                {"name": "Discrimination"},
                {"name": "Story"},
            ],
            templates=[
                {
                    "name": "Dictionary Card",
                    "qfmt": """
<div class=\"card-front\">
    <div class=\"header-center\">
        <div class=\"word\">{{Word}}</div>
        <div class=\"front\">{{Front}}</div>
        <div class=\"pronunciation\">{{Pronunciation}}</div>
    </div>
</div>
""",
                    "afmt": """
{{FrontSide}}
<hr class=\"dashed\">
<div class=\"card-back\">
    <div class=\"ecdict\">{{ECDict}}</div>
    <hr class=\"dashed\">
    <div class=\"ai\">{{AI}}</div>
    <hr class=\"dashed\">
    <div class=\"examples\">{{Youdao}}</div>
    <hr class=\"dashed\">
    <div class=\"discrimination\">{{Discrimination}}</div>
    <hr class=\"dashed\">
    <div class=\"longman\">{{Longman}}</div>
    <hr class=\"dashed\">
    <div class=\"story\">{{Story}}</div>
</div>
""",
                }
            ],
            css="""
.gray { color: #666; }
.phrase-en, .example-en { color: #b22222; font-weight: bold; }
.phrase-cn, .example-cn { color: #1e3a8a; font-weight: bold; }
.discrim-en { color: #0645AD; font-weight: bold; }
.discrim-cn { color: #222; }
.pos-n { color: #d32f2f; font-style: italic; font-weight: bold; }
.story-en { color: #222; }
.story-highlight { color: #d32f2f; font-weight: bold; }
.story-cn-highlight { color: #d32f2f; font-weight: bold; }
.ai-italic { font-style: italic; color: #666; }
/* 虚线分隔符 */
.dashed {
    border: none;
    border-top: 1px dashed var(--divider-color);
    margin: 15px 0;
    width: 100%;
}

/* Front side */
.card-front {
    margin-bottom: 20px;
}

/* Centered header section */
.header-center {
    text-align: center;
    margin-bottom: 20px;
}

.word {
    font-size: 2.2em;
    font-weight: bold;
    color: var(--text-color);
    margin-bottom: 5px;
}

.pronunciation {
    font-size: 1.1em;
    color: var(--highlight-color);
    margin-bottom: 10px;
}

.front {
    color: var(--secondary-text);
    margin-bottom: 15px;
    font-size: 0.90em;
}

/* Back side */
.card-back {
    margin-top: 20px;
}

.ecdict {
    margin: 15px 0;
    text-align: center;
}

.longman {
    margin: 15px 0;
}

.examples {
    color: var(--tertiary-text);
    margin: 15px 0;
}

.examples em {
    color: var(--highlight-color);
    font-style: normal;
    font-weight: bold;
}

.ai {
    color: var(--secondary-text);
    margin: 15px 0;
}

.discrimination {
    color: var(--text-color);
    margin: 15px 0;
}

/* Example sentences */
.example {
    color: var(--tertiary-text);
    margin-left: 20px;
    margin-bottom: 10px;
}

/* Chinese text */
.chinese {
    color: var(--secondary-text);
    margin-left: 20px;
}
            """
            + """
/* Color scheme variables */
:root {
    --bg-color: #ffffff;
    --text-color: #333333;
    --secondary-text: #666666;
    --tertiary-text: #2F4F4F;
    --highlight-color: #0645AD;
    --accent-color: #990000;
    --divider-color: #99a;
    --pos-color: #990000;
    --cn-text-color: #8B008B;
    --phrase-color: #8B4513;
}

/* Dark mode colors */
@media (prefers-color-scheme: dark) {
    .card {
        --bg-color: #1e1e2e;
        --text-color: #e0e0e0;
        --secondary-text: #b0b0b0;
        --tertiary-text: #a0c0c0;
        --highlight-color: #7cb8ff;
        --accent-color: #ff7c7c;
        --divider-color: #666;
        --pos-color: #ff9e64;
        --cn-text-color: #d183e8;
        --phrase-color: #e0c080;
    }
}

/* Night mode in Anki also triggers dark mode */
.nightMode {
    --bg-color: #1e1e2e;
    --text-color: #e0e0e0;
    --secondary-text: #b0b0b0;
    --tertiary-text: #a0c0c0;
    --highlight-color: #7cb8ff;
    --accent-color: #ff7c7c;
    --divider-color: #666;
    --pos-color: #ff9e64;
    --cn-text-color: #d183e8;
    --phrase-color: #e0c080;
}

.card {
    font-family: Arial, sans-serif;
    text-align: left;
    padding: 20px;
    max-width: 800px;
    margin: auto;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}
            """,
        )

    def format_pos(self, text: str) -> str:
        if not text:
            return ""
        text = highlight_pos(text)
        lines = re.split(r'[；;。\n]', text)
        return '<br>'.join(line.strip() for line in lines if line.strip())

    def format_trans(self, translation: str, tense: str, distribution: str) -> str:
        if not tense:
            return f"{translation}<br><br>{distribution}"
        return f"{translation}<br><br>{tense}<br><br>{distribution}"

    def format_youdao(self, data: dict) -> str:
        result = []
        if "example_phrases" in data and data["example_phrases"]:
            result.append("【短语】")
            phrases = []
            for phrase in data["example_phrases"]:
                phrases.append(f"<li><span class='phrase-en'>{phrase['english']}</span> <span class='phrase-cn'>{phrase['chinese']}</span></li>")
            result.append("".join(phrases))
        if "example_sentences" in data and data["example_sentences"]:
            result.append("【例句】")
            phrases = []
            for sentence in data["example_sentences"]:
                phrases.append(f"<li><span class='example-en'>{sentence['english']}</span> <span class='example-cn'>{sentence['chinese']}</span></li>")
            result.append("".join(phrases))
        return "<br>".join(result)

    def format_discrimination(self, text):
        lines = text.split('；')
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'([a-zA-Z0-9\s\(\)\./]+)(.*)', line)
            if m:
                en, cn = m.group(1), m.group(2)
                result.append(f"<span class='discrim-en'>{en.strip()}</span><span class='discrim-cn'>{cn.strip()}</span>")
            else:
                result.append(f"<span class='discrim-cn'>{line}</span>")
        return '<br>'.join(result)

    def add_note(self, data: dict):
        word = ensure_str(data.get("Word", ""))
        pronunciation = ensure_str(data.get('Pronunciation', ''))
        if pronunciation:
            pronunciation = f"[sound:{pronunciation}]"
        ai = data.get('AI', {})
        if ai:
            if 'origin' in ai and 'mnemonic' in ai['origin']:
                ai['origin']['mnemonic']['associative'] = clean_associative(ensure_str(ai['origin']['mnemonic'].get('associative', '')))
            # 统一tenses字段
            if 'origin' in ai and 'tenses' in ai['origin']:
                ai['origin']['tenses'] = format_tenses_field(ai['origin']['tenses'])
            # 词源、助记、辨析用斜体
            for k in ['etymology', 'tenses', 'discrimination']:
                if 'origin' in ai and k in ai['origin']:
                    ai['origin'][k] = wrap_ai_italic(clean_html(ensure_str(ai['origin'][k])))
            if 'discrimination' in ai:
                ai['discrimination'] = wrap_ai_italic(format_discrimination_field(ai['discrimination']))
                ai['discrimination'] = clean_discrimination(clean_html(ensure_str(ai['discrimination'])))
            # 故事内容不用斜体
            if 'story' in ai:
                en = ai['story'].get('english', '')
                zh = ai['story'].get('chinese', '')
                ai['story']['english'] = clean_placeholder(ensure_str(en))
                ai['story']['chinese'] = clean_placeholder(ensure_str(zh))
        ecdict = data.get('ECDict', {})
        for k in ['translation', 'definition', 'diffrentiation']:
            if k in ecdict:
                ecdict[k] = clean_html(clean_stats(ensure_str(ecdict[k])))
        if 'diffrentiation' in ecdict:
            ecdict['diffrentiation'] = clean_discrimination(ensure_str(ecdict['diffrentiation']))
        # 故事高亮目标单词
        story_en = highlight_story_en(ai.get('story', {}).get('english', ''), word)
        story_cn_word = ai.get('story', {}).get('chinese_word', '') if ai.get('story', {}) else ''
        story_cn = highlight_story_cn(ai.get('story', {}).get('chinese', ''), story_cn_word)
        # 所有字段escape非法HTML
        word = escape_invalid_html(word)
        pronunciation = escape_invalid_html(pronunciation)
        story_en = escape_invalid_html(story_en)
        story_cn = escape_invalid_html(story_cn)
        ai_html = ""
        if ai:
            ai_html = f"<span class='gray'>【词源】{ai.get('origin', {}).get('etymology', '')}<br><br>【助记】<li>联想：{ai.get('origin', {}).get('mnemonic', {}).get('associative', '')}</li><li>谐音：{ai.get('origin', {}).get('mnemonic', {}).get('homophone', '')}</li></span>"
        discrim_html = ""
        if ecdict.get("diffrentiation", ""):
            discrim_html = f"【辨析】{self.format_discrimination(ecdict.get('diffrentiation', ''))}"
        note = genanki.Note(
            model=self.model,
            fields=[
                word,
                pronunciation,
                f"[<font color=blue>{ecdict.get('phonetic', '')}</font>] ({ecdict.get('tag', '')} {ecdict.get('bnc', '')}/{ecdict.get('frq', '')})",
                self.format_trans(
                    self.format_pos(ecdict.get("translation", "")),
                    ecdict.get("distribution", ""),
                    ai.get("tenses", ""),
                ),
                f"【英解】<br>{format_definition(ecdict.get('definition', ''))}",
                self.format_youdao(data.get("Youdao", {})),
                ai_html,
                discrim_html,
                f"【故事】 <span class='story-en'>{story_en}</span><br><br><span class='story-cn'>{story_cn}</span>",
            ],
        )
        self.deck.add_note(note)
        self.added = True

    def write_to_file(self, file_path: str, mp3_files):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
