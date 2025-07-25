import genanki


class AnkiDeckCreator:
    def __init__(self, deck_name: str):
        self.deck_name = deck_name
        self.deck_id = 1234567890  # 可以用任意不冲突的数字
        self.model = genanki.Model(
            1305559766,  # model_id
            "Test",  # model_name
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
                        <div class="card-front">
                            <div class="header-center">
                                <div class="word">{{Word}}</div>
                                <div class="front">{{Front}}</div>
                                <div class="pronunciation">[{{Pronunciation}}]</div>
                            </div>
                        </div>
                    """,
                    "afmt": """
                        {{FrontSide}}
                        <hr class="dashed">
                        <div class="card-back">
                            <div class="ecdict">{{ECDict}}</div>
                            <hr class="dashed">
                            <div class="ai">{{AI}}</div>
                            <hr class="dashed">
                            <div class="examples">{{Youdao}}</div>
                            <hr class="dashed">
                            <div class="discrimination">{{Discrimination}}</div>
                            <hr class="dashed">
                            <div class="longman">{{Longman}}</div>
                            <hr class="dashed">
                            <div class="story">{{Story}}</div>
                        </div>
                    """,
                }
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    text-align: left;
                    padding: 20px;
                    max-width: 800px;
                    margin: auto;
                    background-color: white;
                    line-height: 1.6;
                }

                /* 虚线分隔符 */
                .dashed {
                    border: none;
                    border-top: 1px dashed #99a;  /* 使用灰蓝色，更接近图片 */
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
                    color: #000;
                    margin-bottom: 5px;
                }

                .pronunciation {
                    font-size: 1.1em;
                    color: #0645AD;  /* Dictionary blue color */
                    margin-bottom: 10px;
                }

                .front {
                    color: #666;
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
                    color: #2F4F4F;
                    margin: 15px 0;
                }

                .examples em {
                    color: #0645AD;  /* Blue for highlighted terms */
                    font-style: normal;
                    font-weight: bold;
                }

                .ai {
                    color: #666;
                    margin: 15px 0;
                }

                .discrimination {
                    color: #333;
                    margin: 15px 0;
                }

                /* Example sentences */
                .example {
                    color: #2F4F4F;
                    margin-left: 20px;
                    margin-bottom: 10px;
                }

                /* Chinese text */
                .chinese {
                    color: #666;
                    margin-left: 20px;
                }
            """
        )
        self.deck = genanki.Deck(self.deck_id, deck_name)

    def add_note(self, data: dict):
        note = genanki.Note(
            model=self.model,
            fields=[
                data.get("Word", ""),
                data.get("Pronunciation", ""),
                data.get("Front", ""),
                data.get("ECDict", ""),
                data.get("Longman", ""),
                data.get("Youdao", ""),
                data.get("AI", ""),
                data.get("Discrimination", ""),
                data.get("Story", ""),
            ],
        )
        self.deck.add_note(note)
        self.added = True

    def write_to_file(self, file_path: str, mp3_files=None):
        package = genanki.Package(self.deck)
        if mp3_files:
            package.media_files = mp3_files
        package.write_to_file(file_path)
