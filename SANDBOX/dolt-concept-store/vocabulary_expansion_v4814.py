"""
Vocabulary Expansion v4.8.14 — Japanese, Russian, Dutch
========================================================

Three-language expansion targeting the worst-performing languages:
  • ja: 18.8% → target 60%+ via furigana stripping + kanji-only tokenization
  • ru: 16.5% → target 50%+ via Snowball stemmer + stop words + keywords
  • nl: 28.4% → target 55%+ via Snowball stemmer + stop words + keywords

Key architectural decisions:
  1. Japanese: individual hiragana chars are NOT morphemes → skip them.
     Only kanji (CJK Unified) are content words in our atom model.
     Furigana 《》 annotations must be stripped before tokenization.
     OpenCC t2s converts kyūjitai (旧字体) to simplified → matches zh keywords.
  2. Russian: PyStemmer supports 'russian' but was not enabled.
     Many inflected forms (купил→купить, фунтов→фунт) now stem-matchable.
  3. Dutch: PyStemmer supports 'dutch' but was not enabled.
     Critical stop word gap (had, zich, of, zou, mijn were not stop words!).

Agent: GitHub Copilot (Claude Opus 4.6) @ hauru
Session: 2026-02-22 — ja/ru/nl wall breakthrough
"""
import re
from typing import Dict, Set, List

# ═══════════════════════════════════════════════════════════════════════════════
# JAPANESE (ja) — Preprocessing
# ═══════════════════════════════════════════════════════════════════════════════

# Regex for stripping furigana reading annotations in Gutenberg Japanese texts.
# Format: 漢字《ふりがな》 where 《》 brackets contain phonetic readings.
# Also handles special notation: ／″＼ (ditto marks), ＃ (formatting codes).
# Must be applied BEFORE tokenization to avoid counting readings as words.
_FURIGANA_RE = re.compile(r'《[^》]*》')


def strip_furigana(text: str) -> str:
    """Strip furigana reading annotations 《...》 from Japanese text.

    Gutenberg Japanese texts use 《》 to annotate kanji readings:
      其《そ》れ → 其れ
      人々《ひと／″＼》 → 人々
      愚《おろか》 → 愚

    This removes ~20K annotations (51K chars) from a typical text,
    halving the character count and eliminating duplicate hiragana readings.
    """
    return _FURIGANA_RE.sub('', text)


# ═══════════════════════════════════════════════════════════════════════════════
# JAPANESE (ja) — Keywords (kanji not covered by zh keywords)
# ═══════════════════════════════════════════════════════════════════════════════
#
# After OpenCC t2s, these kanji still remain uncovered. Many are common
# in both Japanese and Classical Chinese but weren't in the zh keyword set.
# Categorized by PaniniFS atom ontology (4 categories: ENT, PROC, QUAL, ABS).

KEYWORDS_V4814_JA: Dict[str, List[str]] = {
    # ── ABS (abstracts: numbers, spatial, temporal, relations) ──
    "ABS_NUMBER": [
        "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
        "百", "千", "万", "億", "半", "倍", "数", "幾",
    ],
    "ABS_SPATIAL": [
        "中", "傍", "奥", "外", "内", "辺", "底", "端", "隅", "脇",
        "側", "横", "縦", "先", "向", "背", "裏", "表", "角", "際",
    ],
    "ABS_TEMPORAL": [
        "旦", "昔", "頃", "暫", "刻", "瞬", "永", "久", "既",
        "朝", "夕", "昼", "宵", "暮", "曙", "晩", "午",
    ],
    "ABS_RELATION": [
        "如", "及", "互", "対", "比", "共", "各", "毎", "皆",
        "即", "但", "故", "因", "為", "由", "以",
    ],
    "ABS_QUANTIFIER": [
        "全", "総", "余", "残", "僅", "些", "只", "唯", "殆",
        "甚", "極", "最", "至",
    ],

    # ── ENT (entities: body, nature, artifacts, places) ──
    "ENT_BODY": [
        "肌", "肩", "腕", "胸", "腰", "腹", "背", "膝", "肘",
        "爪", "髪", "眉", "頬", "唇", "額", "顎", "筋", "骨",
        "血", "汗", "涙", "息", "脈",
    ],
    "ENT_NATURE": [
        "霧", "霜", "露", "雲", "嵐", "雷", "虹", "潮", "波",
        "泉", "谷", "丘", "崖", "岸", "浜", "沼", "池",
        "松", "竹", "梅", "桜", "柳", "藤", "蓮", "菊",
    ],
    "ENT_ANIMAL": [
        "蛇", "蟲", "蝶", "蜂", "蟻", "蛙", "亀", "鶴", "鷹",
        "烏", "鳩", "雀", "狐", "狸", "猿", "鹿", "猫", "犬",
        "牛", "馬", "豚", "羊", "鯉", "鯛",
    ],
    "ENT_ARTIFACT": [
        "本", "紙", "筆", "墨", "刀", "鏡", "鐘", "燈", "壺",
        "箱", "袋", "傘", "扇", "帯", "紐", "糸", "針", "布",
        "絹", "綿", "瓦", "柱", "梁", "板", "壁", "屏",
        "琴", "笛", "鼓", "杖", "輿", "舟", "車",
    ],
    "ENT_PLACE": [
        "所", "寺", "宮", "殿", "堂", "塔", "門", "橋", "庭",
        "園", "廊", "廟", "塀", "堀", "郭", "街", "里", "郷",
        "州", "津", "浦", "港", "都", "邑",
    ],
    "ENT_CLOTHING": [
        "衣", "袖", "裾", "襟", "袴", "裃", "着", "被", "纏",
    ],
    "ENT_FOOD": [
        "米", "麦", "豆", "塩", "酒", "茶", "飯", "餅", "汁",
    ],

    # ── PROC (processes: actions, motion, cognition, speech, emotion) ──
    "PROC_MOVE": [
        "居", "込", "去", "戻", "昇", "降", "渡", "越", "抜",
        "迫", "追", "逃", "退", "寄", "離", "浮", "沈", "揺",
        "転", "滑", "跳", "踏", "潜", "漂",
    ],
    "PROC_CONTACT": [
        "付", "掛", "掴", "握", "抱", "押", "引", "投", "振",
        "撃", "叩", "刺", "切", "裂", "砕", "削", "磨", "結",
        "縛", "巻", "折", "曲", "伸", "絞",
    ],
    "PROC_PERCEPT": [
        "覗", "眺", "瞳", "凝", "聴", "嗅", "触", "味", "覚",
        "映", "照", "翳", "蔽",
    ],
    "PROC_COGNIT": [
        "思", "念", "想", "憶", "悟", "解", "察", "覚", "疑",
        "迷", "惑", "忘", "慣", "習", "学",
    ],
    "PROC_SPEECH": [
        "御", "叫", "囁", "呟", "告", "詫", "諭", "誓", "唱",
        "詠", "讃", "嘆", "罵",
    ],
    "PROC_EMOTION": [
        "喜", "哀", "怒", "恋", "慕", "憎", "妬", "羨", "惜",
        "悔", "恥", "誇", "愁", "憂", "嫉",
    ],
    "PROC_POSSESS": [
        "賜", "献", "奉", "貢", "贈", "貰", "借", "貸", "返",
        "盗", "奪", "捨",
    ],
    "PROC_CHANGE": [
        "了", "成", "変", "化", "改", "替", "換", "移", "遷",
        "崩", "壊", "滅", "消", "散", "朽",
    ],
    "PROC_CREATE": [
        "造", "築", "建", "編", "織", "彫", "描", "刻", "塗",
        "染", "焼", "煮", "蒸",
    ],

    # ── QUAL (qualities: appearance, value, sensory) ──
    "QUAL_DIMENSION": [
        "広", "狭", "厚", "薄", "太", "細", "丸", "尖",
        "深", "浅", "遠", "近", "高", "低", "長", "短",
    ],
    "QUAL_PERCEPT": [
        "暗", "眩", "濁", "鮮", "艶", "粗", "滑", "堅", "柔",
        "鈍", "鋭", "甘", "苦", "辛", "酸", "渋", "香",
    ],
    "QUAL_VALUE": [
        "貴", "賤", "尊", "卑", "聖", "俗", "雅", "粋",
        "正", "邪", "善", "悪", "忠", "孝", "仁", "義",
    ],
    "QUAL_TEMPORAL": [
        "若", "幼", "古", "新", "鮮", "朽", "早", "遅",
    ],
    "QUAL_MANNER": [
        "静", "激", "穏", "荒", "烈", "緩", "急", "密", "疎",
    ],

    # ── AGENT (persons, roles) ──
    "AGENT": [
        "私", "自", "己", "我", "吾", "某", "誰",
        "主", "客", "臣", "侍", "僧", "尼", "姫", "翁",
        "師", "弟", "徒", "仲", "敵", "味",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# JAPANESE (ja) — Proper Nouns (character names in the corpus texts)
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4814_JA: List[str] = [
    # Tanizaki 刺靑 and other corpus texts
    "吉", "清", "藤", "松", "竹", "桂", "勘", "徳",
    "太郎", "次郎", "三郎", "五郎",
]

# ═══════════════════════════════════════════════════════════════════════════════
# JAPANESE (ja) — Stop Words (individual hiragana are NOT stop words —
# they are excluded from tokenization entirely. These are multi-char function words)
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4814_JA: List[str] = [
    # Particles and postpositions (single hiragana — as backup in case
    # some slip through the kanji-only filter)
    "は", "が", "を", "に", "で", "と", "も", "の", "へ", "か",
    "ね", "よ", "わ", "な", "ぞ", "ぜ", "さ", "や", "ば", "ら",
    # Multi-character particles and conjunctions
    "から", "まで", "より", "など", "だけ", "ばかり", "ほど",
    "しか", "さえ", "すら", "でも", "だが", "けど", "けれど",
    "ので", "のに", "ため", "ゆえ", "つつ", "ながら",
    # Copula and auxiliaries
    "です", "ます", "ました", "ません", "でした", "ている",
    "である", "であった", "であり", "ではない", "ではなく",
    "だった", "だろう", "でしょう",
    # Common verbs as function words
    "する", "した", "して", "される", "させる", "できる",
    "いる", "いた", "いて", "ある", "あった", "あり",
    "なる", "なった", "なり", "なく", "ない", "なかった",
    # Demonstratives and pronouns
    "これ", "それ", "あれ", "この", "その", "あの", "ここ",
    "そこ", "あそこ", "こう", "そう", "ああ", "どう",
    # Adverbs (function-like)
    "もう", "まだ", "とても", "すでに", "ほとんど", "けっして",
    "ちょうど", "やはり", "ついに", "また", "やがて",
    # Old/classical function words (common in Gutenberg corpus)
    "ゐ", "ゐる", "ゐた", "をり", "なり", "たり", "けり",
    "ぬ", "ず", "べし", "べき", "らむ", "なむ", "かな",
    "ごとく", "ごとし", "やう", "やうな", "やうに",
    # Gutenberg-format markers that appear in Japanese texts
    "＃", "／″＼",
]


# ═══════════════════════════════════════════════════════════════════════════════
# RUSSIAN (ru) — Stop Words
# ═══════════════════════════════════════════════════════════════════════════════
# Missing from the base 50: pronouns (inflected), conjunctions, particles,
# prepositions, auxiliary verb forms.

STOP_WORDS_V4814_RU: List[str] = [
    # Pronouns — oblique cases (nominative forms already in base)
    "меня", "мне", "мной", "мною",  # я
    "тебя", "тебе", "тобой", "тобою",  # ты
    "себя", "себе", "собой", "собою",  # себя (reflexive)
    "нас", "нам", "нами",  # мы
    "вас", "вам", "вами",  # вы
    "ему", "ей", "ним", "нему", "ней",  # он/она oblique
    "них", "ним", "ними",  # они oblique
    "мой", "моя", "моё", "мои", "моего", "моей", "моих",
    "твой", "твоя", "твоё", "твои",
    "свой", "своя", "своё", "свои", "своего", "своей", "своих",
    "наш", "наша", "наше", "наши",
    "ваш", "ваша", "ваше", "ваши",
    "этого", "этой", "этих", "этому", "этим",
    "того", "тому", "тем", "тех",
    "какой", "какая", "какое", "какие",
    "каждый", "каждая", "каждое", "каждые",
    "весь", "вся", "всё", "всех", "всем", "всего",
    "сам", "сама", "само", "сами",
    "другой", "другая", "другое", "другие",
    # Conjunctions and particles
    "если", "хотя", "чтобы", "потому", "поэтому",
    "когда", "пока", "чем", "где", "куда", "откуда",
    "сколько", "столько", "почему",
    "нибудь", "либо", "кто", "никто", "ничто",
    "именно", "лишь", "ведь", "вот", "вон", "ну",
    "даже", "разве", "неужели", "ради",
    # Verb forms of быть (to be) — many missing from base
    "было", "были", "бывает", "бывало", "буду", "будем",
    "будут", "будешь", "будете",
    # Prepositions and their variants
    "ко", "со", "во", "надо", "подо",
    "обо", "ото", "передо",
    # Adverbs that function as discourse markers
    "больше", "меньше", "раньше", "позже", "потом",
    "теперь", "тогда", "здесь", "сюда", "туда", "оттуда",
    "вместе", "отдельно", "совсем", "вовсе",
    "около", "вокруг", "вдоль", "поперёк",
    # Common one-letter prepositions/particles (in case they pass len>=2 filter)
    # These are single chars, so they won't pass the len>=2 content word filter,
    # but including them doesn't hurt.
    "к", "у", "о",
]


# ═══════════════════════════════════════════════════════════════════════════════
# RUSSIAN (ru) — Keywords
# ═══════════════════════════════════════════════════════════════════════════════
# Cyrillic content words for atom coverage. Focus on common words found in
# the corpus that are NOT covered by existing 431 Cyrillic keywords.
# The Snowball stemmer will handle many inflected forms, so we only need
# base forms here.

KEYWORDS_V4814_RU: Dict[str, List[str]] = {
    # ── ABS ──
    "ABS_NUMBER": [
        "один", "два", "три", "четыре", "пять", "шесть", "семь",
        "восемь", "девять", "десять", "двадцать", "тридцать",
        "сорок", "пятьдесят", "сто", "тысяча", "миллион",
        "первый", "второй", "третий", "четвёртый", "пятый",
        "половина", "четверть", "треть", "дюжина", "пара",
    ],
    "ABS_TEMPORAL": [
        "день", "ночь", "утро", "вечер", "час", "минута", "секунда",
        "неделя", "месяц", "год", "век", "эпоха", "пора",
        "весна", "лето", "осень", "зима",
        "понедельник", "вторник", "среда", "четверг",
        "пятница", "суббота", "воскресенье",
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
        "рассвет", "закат", "полдень", "полночь",
        "сегодня", "завтра", "вчера",
    ],
    "ABS_MEASURE": [
        # Standard measures
        "метр", "километр", "сантиметр", "миллиметр",
        "грамм", "килограмм", "тонна", "литр",
        # Old Russian measures (common in Gutenberg texts)
        "аршин", "сажень", "верста", "вершок", "пуд", "фунт",
        "десятина", "четверть",
        # Currency
        "рубль", "копейка", "руб", "коп",
        # Abstract measures
        "цена", "стоимость", "вес", "мера", "размер", "объём",
    ],
    "ABS_SPATIAL": [
        "место", "сторона", "край", "центр", "середина",
        "верх", "низ", "бок", "угол", "дно",
        "север", "юг", "запад", "восток",
        "направление", "расстояние", "глубина", "высота", "ширина",
    ],

    # ── ENT ──
    "ENT_BODY": [
        "голова", "лицо", "глаз", "ухо", "нос", "рот", "губа",
        "рука", "нога", "палец", "плечо", "спина", "грудь",
        "живот", "колено", "локоть", "шея", "горло",
        "сердце", "кровь", "кожа", "волос",
    ],
    "ENT_NATURE": [
        "река", "море", "озеро", "гора", "лес", "поле", "степь",
        "небо", "облако", "ветер", "дождь", "снег", "лёд",
        "трава", "цветок", "дерево", "лист", "корень",
        "берег", "остров", "пустыня", "болото",
    ],
    "ENT_ANIMAL": [
        "лошадь", "конь", "собака", "кошка", "корова", "овца",
        "свинья", "курица", "петух", "гусь", "утка",
        "волк", "медведь", "лиса", "заяц", "олень",
        "орёл", "ворон", "сокол", "голубь",
        "рыба", "змея", "жаба", "бабочка", "пчела",
    ],
    "ENT_ARTIFACT": [
        "дом", "стол", "стул", "дверь", "окно", "стена", "крыша",
        "книга", "письмо", "бумага", "перо", "чернила",
        "нож", "меч", "ружьё", "пушка",
        "одежда", "платье", "рубашка", "шапка", "сапог",
        "сукно", "ткань", "верёвка", "цепь",
        "колесо", "телега", "лодка", "корабль",
        "хлеб", "мясо", "молоко", "масло", "соль", "сахар",
    ],
    "ENT_PLACE": [
        "город", "деревня", "село", "улица", "площадь",
        "церковь", "храм", "дворец", "крепость", "башня",
        "мост", "дорога", "путь", "тропа",
        "комната", "зал", "кухня", "двор", "сад",
        "магазин", "рынок", "лавка", "контора",
    ],

    # ── PROC ──
    "PROC_MOVE": [
        "идти", "ходить", "бежать", "ехать", "лететь", "плыть",
        "стоять", "сидеть", "лежать", "падать", "прыгать",
        "входить", "выходить", "уходить", "приходить",
    ],
    "PROC_SPEECH": [
        "говорить", "сказать", "спросить", "ответить", "кричать",
        "шептать", "молчать", "звать", "петь", "читать", "писать",
        "просить", "приказать", "обещать",
    ],
    "PROC_COGNIT": [
        "думать", "знать", "помнить", "забыть", "понимать",
        "верить", "решить", "считать", "полагать", "сомневаться",
        "мечтать", "воображать", "надеяться",
    ],
    "PROC_EMOTION": [
        "любить", "ненавидеть", "бояться", "радоваться",
        "плакать", "смеяться", "удивляться", "жалеть",
        "страдать", "наслаждаться", "гордиться", "стыдиться",
    ],
    "PROC_PERCEPT": [
        "видеть", "смотреть", "слышать", "слушать",
        "чувствовать", "касаться", "пахнуть",
    ],
    "PROC_POSSESS": [
        "купить", "продать", "платить", "стоить", "получить",
        "взять", "дать", "брать", "отдать", "терять", "найти",
        "торговать", "менять", "должен",
    ],
    "PROC_CHANGE": [
        "начать", "кончить", "продолжать", "остановить",
        "открыть", "закрыть", "разбить", "сломать",
        "расти", "уменьшать", "увеличивать",
    ],

    # ── QUAL ──
    "QUAL_DIMENSION": [
        "большой", "маленький", "длинный", "короткий",
        "широкий", "узкий", "толстый", "тонкий",
        "высокий", "низкий", "глубокий", "мелкий",
    ],
    "QUAL_VALUE": [
        "хороший", "плохой", "дорогой", "дешёвый",
        "добрый", "злой", "справедливый",
        "красивый", "уродливый", "честный",
    ],
    "QUAL_PERCEPT": [
        "белый", "чёрный", "красный", "синий", "зелёный",
        "жёлтый", "серый", "тёмный", "светлый", "яркий",
        "тихий", "громкий", "горячий", "холодный",
        "мягкий", "твёрдый", "сухой", "мокрый",
        "сладкий", "горький", "кислый", "солёный",
    ],
    "QUAL_TEMPORAL": [
        "старый", "молодой", "новый", "древний",
        "быстрый", "медленный", "ранний", "поздний",
    ],

    # ── AGENT ──
    "AGENT": [
        "человек", "мужчина", "женщина", "ребёнок", "мальчик", "девочка",
        "отец", "мать", "сын", "дочь", "брат", "сестра",
        "муж", "жена", "друг", "враг", "сосед",
        "царь", "князь", "солдат", "офицер", "генерал",
        "купец", "крестьянин", "мастер", "учитель", "слуга",
        "господин", "госпожа", "барин", "барыня",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# RUSSIAN (ru) — Proper Nouns
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4814_RU: List[str] = [
    # Common Russian proper nouns in Gutenberg corpus
    "иван", "пётр", "александр", "николай", "михаил",
    "василий", "фёдор", "дмитрий", "андрей", "сергей",
    "мария", "анна", "екатерина", "елена", "ольга",
    "наташа", "соня", "катя", "маша", "саша",
    "москва", "петербург", "россия", "русь",
]


# ═══════════════════════════════════════════════════════════════════════════════
# DUTCH (nl) — Stop Words
# ═══════════════════════════════════════════════════════════════════════════════
# Critical gap: the base nl stop words (51) contain basic articles/prepositions
# but miss many common function words.

STOP_WORDS_V4814_NL: List[str] = [
    # Pronouns — personal (many missing from base)
    "mij", "mijn", "me",
    "jou", "jouw", "uw",
    "zich", "zichzelf",
    "ons", "onze",
    "hen", "hun",
    "wij", "jullie",
    # Demonstratives
    "deze", "dat", "dit", "die",  # some may be in base, safe to re-add
    "zulk", "zulke", "zulks",
    "dergelijk", "dergelijke",
    # Conjunctions and subordinators
    "of", "noch", "doch", "dus", "want",
    "omdat", "doordat", "opdat", "zodat",
    "terwijl", "wanneer", "totdat", "voordat", "nadat",
    "alsof", "hoewel", "ofschoon", "mits",
    "tenzij", "indien", "behalve",
    # Relative pronouns
    "welk", "welke", "wiens", "wier",
    # Prepositions (missing from base)
    "na", "onder", "boven", "tussen", "tegen",
    "langs", "achter", "naast", "binnen", "buiten",
    "tijdens", "volgens", "betreffende", "omtrent",
    "rondom", "voorbij", "sedert", "sinds",
    # Adverbs (function-like)
    "toch", "reeds", "slechts", "echter", "evenwel",
    "bovendien", "trouwens", "immers", "namelijk",
    "daarbij", "daardoor", "daarin", "daarom", "daarop",
    "daarvoor", "daaruit", "daarna", "daarmee",
    "hierin", "hierop", "hiermee", "hierdoor",
    "verder", "eigenlijk", "misschien", "wellicht",
    "zeker", "stellig", "beslist", "bijna", "haast",
    "geheel", "helemaal", "volkomen",
    "altijd", "nooit", "ooit", "dikwijls", "vaak", "zelden",
    "soms", "steeds", "reeds", "alweer",
    # Verb forms of zijn/hebben/worden/zullen (highly frequent)
    "had", "hadden", "heb", "hebt", "heeft", "hebben",
    "ben", "bent", "zijn", "was", "waren", "geweest",
    "zou", "zouden", "zal", "zullen",
    "wordt", "worden", "werd", "werden", "geworden",
    "kan", "kon", "konden", "kunnen", "gekund",
    "mag", "mocht", "mochten", "mogen",
    "moet", "moest", "moesten", "moeten",
    "wil", "wilde", "wilden", "willen",
    "laat", "liet", "lieten", "laten",
    # Negation
    "niet", "geen", "niets", "niemand", "nergens", "nooit",
    # Articles (some missing)
    "der", "des", "den",  # old genitive/dative forms
    # Quantity/degree
    "veel", "weinig", "meer", "meest", "minder", "minst",
    "enkele", "sommige", "alle", "elk", "elke", "ieder", "iedere",
    "enige", "enkel",
    # Discourse markers
    "daar", "hier", "waar", "toen", "nu",
    "nog", "al", "pas", "juist", "net",
    "zonder", "behalve", "ondanks",
    "vóór",
]


# ═══════════════════════════════════════════════════════════════════════════════
# DUTCH (nl) — Keywords
# ═══════════════════════════════════════════════════════════════════════════════
# Dutch content words for atom coverage. With Snowball stemmer now enabled,
# base forms will match inflected corpus forms.

KEYWORDS_V4814_NL: Dict[str, List[str]] = {
    # ── ABS ──
    "ABS_NUMBER": [
        "een", "twee", "drie", "vier", "vijf", "zes", "zeven",
        "acht", "negen", "tien", "twintig", "dertig",
        "honderd", "duizend", "miljoen",
        "eerste", "tweede", "derde", "vierde", "vijfde",
        "helft", "kwart", "derde", "dozijn", "paar",
    ],
    "ABS_TEMPORAL": [
        "dag", "nacht", "ochtend", "middag", "avond",
        "uur", "minuut", "seconde", "moment", "ogenblik",
        "week", "maand", "jaar", "eeuw", "tijdperk",
        "lente", "zomer", "herfst", "winter",
        "vandaag", "morgen", "gisteren",
    ],
    "ABS_SPATIAL": [
        "plaats", "kant", "rand", "midden", "hoek",
        "bovenkant", "onderkant", "zijkant",
        "richting", "afstand", "diepte", "hoogte", "breedte",
    ],

    # ── ENT ──
    "ENT_BODY": [
        "hoofd", "gezicht", "oog", "ogen", "oor", "neus", "mond",
        "hand", "handen", "voet", "voeten", "vinger", "schouder",
        "rug", "borst", "buik", "knie", "arm", "been",
        "hart", "bloed", "huid", "haar",
    ],
    "ENT_NATURE": [
        "rivier", "zee", "meer", "berg", "bos", "veld",
        "hemel", "wolk", "wind", "regen", "sneeuw",
        "gras", "bloem", "boom", "blad", "wortel",
        "zon", "maan", "ster",
    ],
    "ENT_ANIMAL": [
        "paard", "hond", "kat", "koe", "schaap", "varken",
        "kip", "haan", "gans", "eend",
        "wolf", "beer", "vos", "haas", "hert",
        "vogel", "vis", "slang",
    ],
    "ENT_ARTIFACT": [
        "huis", "tafel", "stoel", "deur", "venster", "raam",
        "boek", "brief", "papier", "pen",
        "mes", "zwaard", "geweer",
        "kleed", "jurk", "hemd", "hoed", "schoen",
        "wiel", "wagen", "boot", "schip",
        "brood", "vlees", "melk", "boter", "zout", "suiker",
    ],
    "ENT_PLACE": [
        "stad", "dorp", "straat", "plein",
        "kerk", "paleis", "kasteel", "toren",
        "brug", "weg", "pad",
        "kamer", "zaal", "keuken", "tuin",
        "winkel", "markt",
    ],

    # ── PROC ──
    "PROC_MOVE": [
        "gaan", "lopen", "rennen", "rijden", "vliegen", "zwemmen",
        "staan", "zitten", "liggen", "vallen", "springen",
        "komen", "vertrekken", "terugkeren",
    ],
    "PROC_SPEECH": [
        "zeggen", "spreken", "vragen", "antwoorden", "roepen",
        "fluisteren", "zwijgen", "zingen", "lezen", "schrijven",
    ],
    "PROC_COGNIT": [
        "denken", "weten", "herinneren", "vergeten", "begrijpen",
        "geloven", "beslissen", "twijfelen",
        "dromen", "hopen", "vrezen",
    ],
    "PROC_EMOTION": [
        "houden", "haten", "vrezen", "verheugen",
        "huilen", "lachen", "verwonderen",
        "lijden", "genieten", "schamen",
        "vreugde", "verdriet", "vrees", "woede",
    ],
    "PROC_PERCEPT": [
        "zien", "kijken", "horen", "luisteren",
        "voelen", "ruiken", "proeven",
    ],
    "PROC_POSSESS": [
        "kopen", "verkopen", "betalen", "kosten",
        "nemen", "geven", "ontvangen", "verliezen", "vinden",
        "handel", "commercie", "winst", "verlies",
    ],
    "PROC_CHANGE": [
        "beginnen", "eindigen", "stoppen",
        "openen", "sluiten", "breken",
        "groeien", "bouwen", "maken",
    ],

    # ── QUAL ──
    "QUAL_DIMENSION": [
        "groot", "klein", "lang", "kort",
        "breed", "smal", "dik", "dun",
        "hoog", "laag", "diep", "ondiep",
    ],
    "QUAL_VALUE": [
        "goed", "slecht", "mooi", "lelijk",
        "duur", "goedkoop", "eerlijk", "rechtvaardig",
    ],
    "QUAL_PERCEPT": [
        "wit", "zwart", "rood", "blauw", "groen",
        "geel", "grijs", "donker", "licht", "helder",
        "stil", "luid", "warm", "koud",
        "zacht", "hard", "droog", "nat",
        "zoet", "bitter", "zuur",
    ],
    "QUAL_TEMPORAL": [
        "oud", "jong", "nieuw", "snel", "langzaam",
    ],

    # ── AGENT ──
    "AGENT": [
        "mens", "man", "vrouw", "kind", "jongen", "meisje",
        "vader", "moeder", "zoon", "dochter", "broer", "zuster",
        "echtgenoot", "echtgenote", "vriend", "vijand", "buur",
        "koning", "koningin", "prins", "prinses", "ridder",
        "soldaat", "officier", "generaal",
        "koopman", "boer", "meester", "leraar", "knecht",
        "heer", "dame", "mevrouw",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# DUTCH (nl) — Proper Nouns
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4814_NL: List[str] = [
    # Names from the Dutch corpus texts
    "massijn", "fietje", "akspoele", "potvlieghe",
    "fortuné", "eulalie", "spittael",
    # Common Dutch proper nouns
    "jan", "piet", "klaas", "hendrik", "willem",
    "amsterdam", "rotterdam", "brussel", "antwerpen",
    "nederland", "holland", "vlaanderen", "belgie",
]


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_keywords_v4814() -> Dict[str, Dict[str, List[str]]]:
    """Return keywords by language → atom → keyword list."""
    return {
        "ja": KEYWORDS_V4814_JA,
        "ru": KEYWORDS_V4814_RU,
        "nl": KEYWORDS_V4814_NL,
    }


def get_stop_words_v4814() -> Dict[str, List[str]]:
    """Return stop words by language."""
    return {
        "ja": STOP_WORDS_V4814_JA,
        "ru": STOP_WORDS_V4814_RU,
        "nl": STOP_WORDS_V4814_NL,
    }


def get_proper_nouns_v4814() -> Dict[str, List[str]]:
    """Return proper nouns by language."""
    return {
        "ja": PROPER_NOUNS_V4814_JA,
        "ru": PROPER_NOUNS_V4814_RU,
        "nl": PROPER_NOUNS_V4814_NL,
    }
