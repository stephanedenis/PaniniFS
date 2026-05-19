"""Vocabulary expansion v4.8.16 — Russian pre-reform orthography + RU/NL deep expansion.

Three main interventions:
1. Pre-reform Russian orthography normalizer (pre-1918 spelling → modern)
   - Strips trailing ъ (hard sign after consonants)
   - ѣ → е (yat), і → и (decimal i), ѳ → ф (fita), ѵ → и (izhitsa)
   - Enables Snowball stemmer to work on pre-reform texts (pg30774)

2. Massive Russian vocabulary expansion (~450 keywords, ~250 stop words)
   - Religious/spiritual: бог, дух, душа, творец, ангел, грех, etc.
   - Nature/cosmos: солнце, звезда, луч, небо, холм, etc.
   - Abstract: свет, мрак, время, вечность, образ, etc.
   - Literary/poetic: глас, песнь, лира, арфа, хор, etc.

3. Massive Dutch vocabulary expansion (~350 keywords, ~180 stop words)
   - Navigation/exploration: eiland, schip, haven, vloot, etc.
   - Common verbs (past tense irregular): kwam, sprak, liep, etc.
   - Old spelling forms: groote, schoone, spaansche, zoo, etc.

Corpus targets:
  pg14741 (ru, Derzhavin odes) — 21.8% → target 55%+
  pg30774 (ru, pre-reform travel accounts) — 13.6% → target 45%+
  pg17525 (nl, Buysse) — 41.7% → target 55%+
  pg18066 (nl, Columbus) — 37.9% → target 55%+

Author: Copilot (Claude Opus 4.6) — session hauru 2026-02-23
"""

import re as _re

# ═══════════════════════════════════════════════════════════════════════════════
# PRE-REFORM RUSSIAN ORTHOGRAPHY NORMALIZER
# ═══════════════════════════════════════════════════════════════════════════════

# Pre-1918 Russian used: ъ at end of words, ѣ (yat), і (decimal i), ѳ (fita)
# The 1918 reform abolished all of these, replacing with modern equivalents.
_PREREFORM_MAP = str.maketrans("ѣіѳѵ", "еифи")


def normalize_prereform_ru(word: str) -> str:
    """Normalize pre-1918 Russian orthography to modern.

    Transformations:
    - Strip trailing ъ (hard sign) — mandatory after final consonants pre-1918
    - ѣ → е (yat → ye)
    - і → и (decimal i → и)
    - ѳ → ф (fita → ef)
    - ѵ → и (izhitsa → и) — very rare
    - -аго → -ого (pre-reform genitive adjective ending)
    - -яго → -его (pre-reform genitive adjective ending, soft variant)

    Safe: trailing ъ stripping won't affect modern words (ъ never ends modern words;
    in modern Russian ъ only appears medially in compounds like объявить, подъём).
    """
    word = word.translate(_PREREFORM_MAP)
    if word.endswith("ъ"):
        word = word[:-1]
    # Pre-reform genitive adjective endings: -аго → -ого, -яго → -его
    if word.endswith("аго") and len(word) > 3:
        word = word[:-3] + "ого"
    elif word.endswith("яго") and len(word) > 3:
        word = word[:-3] + "его"
    return word


# Regex to detect pre-reform text features
_PREREFORM_CHARS_RE = _re.compile(r"[ѣіѳѵ]|ъ\b")


def has_prereform_features(text: str) -> bool:
    """Quick check if a text contains pre-reform Russian orthography features."""
    return bool(_PREREFORM_CHARS_RE.search(text))


# ═══════════════════════════════════════════════════════════════════════════════
# OLD DUTCH SPELLING NORMALIZATION (pre-1947 reform)
# ═══════════════════════════════════════════════════════════════════════════════

# Common old→modern Dutch spelling mappings found in corpus
OLD_DUTCH_SPELLING = {
    # Double vowel before consonant → single vowel in open syllable
    "zoo": "zo",
    "zooals": "zoals",
    "zooveel": "zoveel",
    "zoodanig": "zodanig",
    "zoogenaamd": "zogenaamd",
    "zoodra": "zodra",
    "zoozeer": "zozeer",
    "hoe": "hoe",
    # -sch- adjective endings
    "spaansche": "spaanse",
    "russische": "russische",
    "europeësche": "europese",
    "europeesche": "europese",
    "indische": "indische",
    "hollandsche": "hollandse",
    "engelsche": "engelse",
    "fransche": "franse",
    "duitsche": "duitse",
    "italiaansche": "italiaanse",
    "portugeesche": "portugese",
    "afrikaansche": "afrikaanse",
    "turksche": "turkse",
    "chineesche": "chinese",
    "japansche": "japanse",
    "arabische": "arabische",
    "christelyke": "christelijke",
    "koninklyke": "koninklijke",
    "mogelyke": "mogelijke",
    "natuurlyke": "natuurlijke",
    "werkelyke": "werkelijke",
    "eigenlyke": "eigenlijke",
    "heerlyk": "heerlijk",
    "mogelyk": "mogelijk",
    "natuurlyk": "natuurlijk",
    "werkelyk": "werkelijk",
    "eigenlyk": "eigenlijk",
    # -oo- in closed syllables (old: groote, new: grote)
    "groote": "grote",
    "grooten": "groten",
    "schoone": "schone",
    "schoonen": "schonen",
    "hooge": "hoge",
    "hoogen": "hogen",
    "doode": "dode",
    "dooden": "doden",
    "bloote": "blote",
    "blooten": "bloten",
    "noodige": "nodige",
    "noodzakelyke": "noodzakelijke",
}


# ═══════════════════════════════════════════════════════════════════════════════
# RUSSIAN KEYWORDS (v4.8.16) — mapped to ontological atoms
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4816_RU = {
    "ru": {
        # === ENT (entities — objects, substances) ===
        "ENT_CELESTIAL": [
            "солнце", "луна", "звезда", "луч", "небо", "небеса",
            "заря", "рассвет", "закат", "зенит", "созвездие",
            "комета", "светило", "денница",
        ],
        "ENT_NATURE": [
            "гора", "холм", "скала", "утёс", "бездна", "пропасть",
            "долина", "поле", "степь", "пустыня", "лес", "роща",
            "берег", "остров", "пещера", "брег",
        ],
        "ENT_WATER": [
            "море", "река", "океан", "озеро", "источник", "ручей",
            "поток", "водопад", "волна", "пучина", "влага", "роса",
        ],
        "ENT_ELEMENT": [
            "огонь", "пламя", "пожар", "искра", "молния", "гром",
            "ветер", "буря", "вихрь", "туча", "облако", "дождь",
            "снег", "лёд", "мороз",
        ],
        "ENT_BODY": [
            "тело", "плоть", "кровь", "кость", "сердце", "глаз",
            "рука", "нога", "голова", "лицо", "уста", "грудь",
            "чело", "перст", "длань", "очи", "десница", "лоно",
            "утроба", "персть", "прах",
        ],
        "ENT_ARTIFACT": [
            "меч", "щит", "копьё", "лук", "стрела", "оружие",
            "корона", "венец", "скипетр", "трон", "престол",
            "храм", "алтарь", "жертвенник", "крест", "чаша",
            "хлеб", "вино", "елей", "кадило",
            "чертог", "дворец", "башня", "врата", "стена",
            "колокол", "цепь", "оковы", "гроб", "могила",
        ],
        "ENT_INSTRUMENT": [
            "арфа", "лира", "труба", "орган", "тимпан", "кимвал",
            "псалтирь", "гусли", "свирель", "цевница",
        ],
        "ENT_CREATURE": [
            "ангел", "серафим", "херувим", "архангел", "демон",
            "тварь", "зверь", "змей", "змея", "орёл", "голубь",
            "агнец", "лев", "конь", "овца", "вол",
        ],
        "ENT_FLORA": [
            "дерево", "цветок", "роза", "лилия", "трава",
            "колос", "нива", "сад", "виноград", "плод",
            "лавр", "кедр", "пальма", "терн",
        ],
        "ENT_COVERING": [
            "покров", "завеса", "одежда", "риза", "покрывало",
            "облачение", "порфира", "багряница",
        ],
        "ENT_SUSTENANCE": [
            "пища", "хлеб", "вода", "вино", "мёд", "молоко",
            "манна", "трапеза",
        ],
        "ENT_PLACE": [
            "город", "село", "край", "страна", "царство",
            "земля", "мир", "вселенная", "отечество", "родина",
            "пустынь", "обитель", "рай", "ад", "преисподняя",
        ],
        "ENT_PERSON": [
            "народ", "люди", "человек", "муж", "жена", "дитя",
            "старец", "юноша", "дева", "вдова", "сирота",
            "раб", "пленник", "странник", "пришелец",
            "воин", "герой", "витязь", "богатырь",
        ],
        # === PROC (processes — actions, events, emotions) ===
        "PROC_RELIGIOUS": [
            "молитва", "хвала", "псалом", "пение", "славословие",
            "жертва", "покаяние", "исповедь", "крещение",
            "причастие", "благословение", "проповедь", "пророчество",
        ],
        "PROC_SPIRITUAL": [
            "грех", "искупление", "спасение", "воскресение",
            "преображение", "вознесение", "сошествие",
            "откровение", "чудо", "знамение", "видение",
        ],
        "PROC_EMOTION": [
            "любовь", "ненависть", "радость", "печаль", "горе",
            "скорбь", "тоска", "грусть", "отчаяние", "надежда",
            "страх", "ужас", "трепет", "восторг", "блаженство",
            "гнев", "ярость", "месть", "ревность", "зависть",
            "жалость", "сострадание", "умиление",
        ],
        "PROC_COGNITION": [
            "мысль", "разум", "ум", "рассудок", "премудрость",
            "знание", "истина", "правда", "ложь", "заблуждение",
            "вера", "сомнение", "убеждение",
        ],
        "PROC_ACTION": [
            "битва", "война", "победа", "поражение",
            "суд", "казнь", "наказание", "кара",
            "дело", "труд", "подвиг", "деяние",
            "путешествие", "странствие", "плавание",
        ],
        "PROC_CHANGE": [
            "смерть", "жизнь", "рождение", "конец",
            "начало", "создание", "разрушение", "гибель",
            "падение", "восстание", "возрождение",
        ],
        "PROC_MOVEMENT": [
            "полёт", "бег", "шествие", "восхождение",
            "сошествие", "нисхождение", "вторжение",
        ],
        "PROC_SOUND": [
            "глас", "голос", "крик", "вопль", "стон",
            "песнь", "гимн", "хор", "звон", "гром",
            "шум", "гул", "рёв", "шёпот",
        ],
        "PROC_PERCEPTION": [
            "взор", "взгляд", "зрение", "слух",
            "лик", "образ", "вид", "зрелище",
        ],
        # === QUAL (qualities — properties, attributes) ===
        "QUAL_DIVINE": [
            "святой", "священный", "праведный", "благой",
            "вечный", "бессмертный", "всесильный", "всемогущий",
            "всеведущий", "премудрый", "пресветлый",
            "блаженный", "преблаженный",
        ],
        "QUAL_MORAL": [
            "добрый", "злой", "грешный", "праведный",
            "чистый", "нечистый", "невинный", "виновный",
            "верный", "неверный", "справедливый",
            "милосердный", "жестокий", "кроткий", "смиренный",
        ],
        "QUAL_INTENSITY": [
            "великий", "могучий", "сильный", "слабый",
            "огромный", "бесконечный", "безмерный",
            "грозный", "страшный", "ужасный", "дивный",
            "чудный", "славный", "прекрасный",
        ],
        "QUAL_LIGHT": [
            "светлый", "тёмный", "яркий", "тусклый",
            "блестящий", "сияющий", "лучезарный", "мрачный",
        ],
        "QUAL_TEMPORAL": [
            "древний", "вечный", "бессмертный",
            "краткий", "мимолётный", "смертный",
        ],
        # === ABS (abstracts — relations, structures, measures) ===
        "ABS_ABSTRACT": [
            "свет", "тьма", "мрак", "тень",
            "добродетель", "порок", "благость", "милость",
            "слава", "честь", "бесчестие",
            "сила", "власть", "могущество", "величие",
            "красота", "уродство", "гармония",
        ],
        "ABS_STRUCTURE": [
            "закон", "заповедь", "завет", "обет",
            "предел", "граница", "мера", "число",
            "круг", "путь", "дорога", "стезя",
            "основание", "вершина", "глубина", "высота",
        ],
        "ABS_TEMPORAL": [
            "время", "вечность", "миг", "мгновение", "час",
            "день", "ночь", "утро", "вечер",
            "век", "эпоха", "эра", "столетие",
        ],
        "ABS_SOCIAL": [
            "царь", "князь", "король", "император",
            "судья", "пророк", "священник", "апостол",
            "святой", "мученик", "праведник",
            "раб", "господин", "слуга", "владыка",
        ],
        # === AGENT (specific religious/literary agents) ===
        "AGENT": [
            "бог", "господь", "творец", "создатель", "вседержитель",
            "всевышний", "саваоф", "иегова",
            "христос", "спаситель", "искупитель", "мессия",
            "дух", "душа", "дух святой",
            "сатана", "дьявол", "лукавый",
        ],
        # === Additional forms needed for stemmer coverage ===
        # (Stemmer gives different stems for vocative/oblique forms)
        "AGENT_FORMS": [
            "боже", "божий", "божие", "божья", "божьей",
            "творца", "творцу", "творцом", "творцы",
            "господа", "господу", "господом",
            "ангелы", "ангелов", "ангелом",
        ],
        # === Words appearing frequently in corpus but missed in main lists ===
        "PROC_SPEECH_EXTRA": [
            "поет", "пой", "воскликни", "зрит", "зрю",
            "вижу", "глядит", "глядел", "льет", "льёт",
            "дает", "даёт", "раздается", "раздаётся",
            "послан", "посланник", "посланный",
            "взяв", "взять", "взял",
        ],
        "ENT_EXTRA": [
            "сонм", "сонмы", "сонмов",
            "огнь", "огонь",
            "тьма", "тьмы",
            "дни", "дней", "днем",
            "чудес", "чудо", "чудеса",
            "злых", "злой", "зло", "зла", "зол",
            "бед", "беда", "бедствие",
            "тварь", "тварей",
            "вельможа", "вельмож",
            "награда", "награды",
            "чувство", "чувств",
        ],
        "QUAL_EXTRA": [
            "блажен", "блаженна", "блаженны",
            "полн", "полный", "полна",
            "жив", "живой", "живые",
            "строг", "строга", "строгий",
            "един", "единый", "единственный",
            "смертный", "смертных", "смертен",
        ],
        "ABS_EXTRA": [
            "блеск", "сияние", "сиять",
            "покой", "покоя", "покоем",
            "помощь", "помощи", "помощью",
            "милость", "милости", "милостью",
            "вечность", "вечности",
            "добродетель", "добродетели",
            "премудрость", "премудрости",
            "предел", "пределы", "пределов",
            "судьба", "судеб", "судьбы",
            "конец", "конца",
            "лик", "лики", "ликов",
            "образ", "образы", "образов",
            "честь", "чести", "честью",
            "имя", "имени", "именем",
            "холм", "холмы", "холмов",
            "вождь", "вожди", "вождей",
        ],
        # === pg30774 historical/cultural vocabulary ===
        "PROC_HISTORICAL": [
            "посольство", "посольства", "послов",
            "торжество", "торжества",
            "аудиенция", "аудиенции",
            "величество", "величества",
            "дневник", "дневника",
            "хроника", "хроники",
            "издание", "издания",
            "гравюра", "гравюры", "гравюр",
            "рисунок", "рисунков",
            "библиотека", "библиотеке",
            "собрание", "собрания",
        ],
        "QUAL_HISTORICAL": [
            "русский", "русская", "русское",
            "русские", "русских", "русскаго", "русского",
            "иностранный", "иностранцев", "иностранцы",
            "великий", "великого", "великаго",
            "царский", "царское", "царского", "царскаго",
            "драгоценный", "драгоценными", "драгоценные",
        ],
        "ENT_HISTORICAL": [
            "стрельцы", "стрельцов", "стрелец",
            "всадник", "всадники",
            "камень", "камни", "камнями",
            "население", "населения",
            "нравы", "нравов",
            "европа", "история", "истории",
            "водоосвящение", "водоосвящения",
            "вербное", "казнь", "казни",
        ],
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# DUTCH KEYWORDS (v4.8.16) — mapped to ontological atoms
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4816_NL = {
    "nl": {
        # === ENT (entities) ===
        "ENT_MARITIME": [
            "eiland", "eilanden", "schip", "schepen", "haven", "havens",
            "vloot", "boot", "boten", "kano", "bark", "fregat",
            "boord", "anker", "zeil", "zeilen", "mast", "roer",
            "kompas", "kaart", "kaarten",
        ],
        "ENT_GEOGRAPHY": [
            "kust", "kusten", "berg", "bergen", "rivier", "rivieren",
            "zee", "oceaan", "baai", "kaap", "golf",
            "bos", "bossen", "dal", "vlakte", "woestijn",
            "strand", "oever", "kreek",
        ],
        "ENT_SETTLEMENT": [
            "stad", "steden", "dorp", "dorpen", "nederzetting",
            "kolonie", "vesting", "fort", "kasteel",
            "huis", "huizen", "kerk", "kerken", "paleis",
            "herberg", "tempel", "moskee",
        ],
        "ENT_PERSON": [
            "koning", "koningin", "prins", "prinses",
            "admiraal", "kapitein", "gouverneur", "generaal",
            "soldaat", "soldaten", "zeeman", "zeelieden",
            "priester", "monnik", "bisschop", "paus",
            "opperhoofd", "hoofdman", "leider", "aanvoerder",
            "vrouw", "vrouwen", "meisje", "jongen",
            "inboorling", "inboorlingen", "inlander", "inlanders",
            "slaaf", "slaven", "gevangene", "gevangenen",
            "meneer", "juffrouw", "juffrouwen", "heer", "dame",
            "neger", "negers", "negerknecht",
            "gepeupel", "menigte", "volk", "volken",
            "weduwe", "bedelaar", "boer", "boeren",
        ],
        "ENT_OBJECT": [
            "goud", "zilver", "parel", "parelen", "diamant",
            "kruid", "kruiden", "specerij", "specerijen",
            "wapen", "wapens", "zwaard", "kanon", "kanonnen",
            "bevel", "bevelen", "brief", "brieven",
            "vlag", "vaandel", "kruis",
            "geschenk", "geschenken", "tribuut",
            "rijtuig", "paard", "paarden", "koets",
        ],
        "ENT_FOOD": [
            "voedsel", "brood", "water", "wijn", "vis", "vissen",
            "fruit", "graan", "mais", "tabak", "katoen",
        ],
        "ENT_NATURE": [
            "zon", "maan", "ster", "sterren",
            "wind", "storm", "regen", "bliksem", "donder",
            "boom", "bomen", "bloem", "bloemen", "gras",
            "vogel", "vogels", "vis", "vissen", "hond", "honden",
        ],
        "ENT_BODY": [
            "hoofd", "hand", "handen", "voet", "voeten",
            "oog", "ogen", "oor", "oren", "mond",
            "hart", "bloed", "been", "benen", "arm", "armen",
        ],
        "ENT_ABSTRACT": [
            "naam", "namen", "woord", "woorden", "taal",
            "verhaal", "verhalen", "brief", "brieven",
            "wet", "wetten", "recht", "rechten",
            "geld", "prijs", "kosten", "waarde",
        ],
        # === PROC (processes) ===
        "PROC_MOVEMENT": [
            # Infinitives + irregular past tenses (stemmer can't reduce these)
            "komen", "kwam", "kwamen", "gekomen",
            "gaan", "ging", "gingen", "gegaan",
            "lopen", "liep", "liepen", "gelopen",
            "rijden", "reed", "reden", "gereden",
            "varen", "voer", "voeren", "gevaren",
            "zeilen", "sturen", "landen", "vertrekken",
            "terugkeren", "naderen", "vluchten",
        ],
        "PROC_COMMUNICATION": [
            "spreken", "sprak", "spraken", "gesproken",
            "zeggen", "zei", "zeiden", "gezegd",
            "roepen", "riep", "riepen", "geroepen",
            "noemen", "noemde", "noemden", "genoemd",
            "antwoorden", "antwoordde",
            "vertellen", "vertelde", "schrijven", "schreef",
            "bevelen", "beval", "verklaren", "verklaarde",
            "vragen", "vroeg", "vroegen", "gevraagd",
        ],
        "PROC_PERCEPTION": [
            "zien", "zag", "zagen", "gezien",
            "kijken", "keek", "gekeken",
            "horen", "hoorde", "gehoord",
            "voelen", "voelde", "gevoeld",
            "schijnen", "scheen", "geschenen",
            "blijken", "bleek", "gebleken",
            "merken", "merkte", "opmerken",
        ],
        "PROC_ACQUISITION": [
            "vinden", "vond", "vonden", "gevonden",
            "krijgen", "kreeg", "kregen", "gekregen",
            "geven", "gaf", "gaven", "gegeven",
            "nemen", "nam", "namen", "genomen",
            "brengen", "bracht", "brachten", "gebracht",
            "sturen", "stuurde", "zenden", "zond", "zonden", "gezonden",
            "ontvangen", "ontving",
        ],
        "PROC_STATE": [
            "blijven", "bleef", "bleven", "gebleven",
            "staan", "stond", "stonden", "gestaan",
            "zitten", "zat", "zaten", "gezeten",
            "liggen", "lag", "lagen", "gelegen",
            "houden", "hield", "hielden", "gehouden",
            "doen", "deed", "deden", "gedaan",
            "beginnen", "begon", "begonnen",
            "laten", "liet", "lieten", "gelaten",
            "weten", "wist", "wisten", "geweten",
            "kennen", "kende", "gekend",
        ],
        "PROC_CHANGE": [
            "sterven", "stierf", "gestorven",
            "doden", "doodde", "gedood",
            "breken", "brak", "gebroken",
            "bouwen", "bouwde", "gebouwd",
            "verwoesten", "verwoestte", "vernietigen",
            "veroveren", "veroverde",
            "ontdekken", "ontdekte", "ontdekking",
        ],
        "PROC_EMOTION": [
            "hopen", "vrezen", "verlangen", "wensen",
            "geloven", "geloofde", "vertrouwen",
            "bewonderen", "bewonderde",
            "verschrikken", "verschrikte",
        ],
        # === QUAL (qualities) ===
        "QUAL_SIZE": [
            "groot", "groote", "grote", "grooten", "groten",
            "grootste", "klein", "kleine", "kleinste",
            "lang", "lange", "kort", "korte",
            "breed", "brede", "diep", "diepe",
            "hoog", "hooge", "hoge",
            "wijd", "wijde", "smal", "smalle",
        ],
        "QUAL_APPEARANCE": [
            "mooi", "mooie", "schoon", "schoone", "schone",
            "lelijk", "fraai", "fraaie", "prachtig",
            "nieuw", "nieuwe", "oud", "oude", "ouder",
            "jong", "jonge", "blank", "donker",
            "wit", "witte", "zwart", "zwarte",
            "rood", "rode", "groen", "groene", "blauw", "blauwe",
            "geel", "gele",
        ],
        "QUAL_QUANTITY": [
            "veel", "vele", "velen", "weinig",
            "enkele", "talrijk", "talrijke",
            "enorm", "enorme", "gehele",
            "laatste", "eerste", "tweede", "derde",
            "volgende", "vorige",
        ],
        "QUAL_MANNER": [
            "snel", "snelle", "langzaam", "langzame",
            "spoedig", "plotseling", "eensklaps",
            "voortdurend", "voortdurende",
            "bepaald", "bepaalde",
            "heftig", "heftige", "hevig", "hevige",
        ],
        "QUAL_EVALUATION": [
            "goed", "goede", "slecht", "slechte",
            "rijk", "rijke", "arm", "arme",
            "sterk", "sterke", "zwak", "zwakke",
            "machtig", "machtige", "vijandig", "vijandige",
            "vriendelijk", "vriendelijke", "wreed", "wrede",
            "wild", "wilde", "beschaafd",
        ],
        # === ABS (abstracts) ===
        "ABS_TEMPORAL": [
            "tijd", "tijden", "dag", "dagen",
            "nacht", "nachten", "morgen", "avond",
            "week", "weken", "maand", "maanden",
            "jaar", "jaren", "eeuw", "eeuwen",
            "uur", "uren", "ogenblik",
        ],
        "ABS_SPATIAL": [
            "plaats", "plaatsen", "kant", "kanten",
            "richting", "afstand", "mijl", "mijlen",
            "weg", "wegen", "pad", "paden",
            "grens", "grenzen", "gebied", "gebieden",
        ],
        "ABS_SOCIAL": [
            "macht", "gezag", "heerschappij",
            "handel", "koophandel", "koopman",
            "reis", "reizen", "tocht", "tochten",
            "expeditie", "ontdekkingsreis",
            "beschaving", "cultuur", "godsdienst",
            "vrijheid", "gerechtigheid", "wraak",
            "vrede", "oorlog", "opstand", "strijd",
            "verdrag", "verbond", "overeenkomst",
            "torenhoog", "torment",
        ],
        "ABS_ABSTRACT": [
            "gelijk", "soort", "soorten", "aard",
            "voorbeeld", "bewijs", "bewijzen",
            "reden", "oorzaak", "gevolg",
            "doel", "bedoeling", "plan",
            "kracht", "invloed",
            "voordeel", "nadeel", "gevaar",
        ],
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
# RUSSIAN STOP WORDS (v4.8.16)
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4816_RU = [
    # === Personal pronouns (all cases) ===
    "ты", "тебя", "тебе", "тобой", "тобою",
    "мы", "нас", "нам", "нами",
    "вы", "вас", "вам", "вами",
    # он/она/оно/они oblique cases not already in v4814
    "им", "ими", "нем", "нём", "нему",
    "него", "нее", "неё", "ней",
    "ее", "её",
    # === Demonstrative pronouns ===
    "сей", "сия", "сие", "сего", "сему", "сих", "сим",
    "тот", "та", "те", "того", "той", "тех", "тем", "тому",
    "этот", "эта", "это", "этого", "этой", "этих", "этим", "этому",
    "оный", "оная", "оное", "оного", "оных", "оным",
    # === Relative/interrogative pronouns ===
    "который", "которая", "которое", "которые",
    "которого", "которой", "которых", "которому", "которым",
    "кем", "кого", "кому", "чего", "чем", "чему",
    # === Prepositions (not already present) ===
    "пред", "перед", "передо",
    "под", "подо",
    "над", "надо",
    "меж", "между",
    "сквозь", "чрез", "через",
    "мимо", "вдоль", "вокруг", "вкруг",
    "внутрь", "вовне", "поверх", "посреди",
    "ради", "подле", "возле",
    # === Particles ===
    "да", "нет", "ни", "ль", "ли",
    "же", "ведь", "бы", "уж", "уже",
    "вот", "вон", "ну", "лишь", "только",
    "ещё", "еще",
    # === Conjunctions (not already present) ===
    "чтоб", "чтобы", "дабы", "ибо",
    "будто", "словно", "якобы",
    "хотя", "хоть", "хотя бы",
    "пусть", "пускай",
    "иль", "или", "либо",
    "притом", "причём", "причем",
    # === Archaic/Church Slavonic particles ===
    "яко", "яже", "иже", "еже",
    "сый", "сущий",
    "бысть", "несть",
    "паче", "почто", "зане", "понеже",
    "аще", "токмо", "елико",
    "се", "сиречь", "такожде",
    "ово", "убо",
    # === Interjections ===
    "ах", "ох", "увы", "ой", "эй",
    "о", "ого", "ура",
    # === Adverbs (function-like) ===
    "всегда", "везде", "всюду", "нигде", "никогда",
    "вдруг", "прочь",
    "ввек", "вовек", "вовеки",
    "тут", "там", "здесь", "сюда", "туда", "оттуда", "отсюда",
    "можно", "надо", "нужно", "нельзя",
    "самый", "сам", "сама", "само", "сами",
    "наш", "наша", "наше", "наши", "наших", "нашим", "нашей", "нашему",
    "ваш", "ваша", "ваше", "ваши", "ваших", "вашим", "вашей", "вашему",
    "свой", "своя", "своё", "свои", "своего", "своей", "своих", "своим",
    "своими", "своему", "свою",
    "мой", "моя", "моё", "мои", "моего", "моей", "моих", "моим", "мою", "моем",
    "твой", "твоя", "твоё", "твои", "твоего", "твоей", "твоих", "твоим",
    "твою", "твоем", "твоему", "твоими",
    # === Biblical abbreviations (appear as markers, not content) ===
    "ст", "гл", "матф", "иоан", "пс", "ис",
    # === Суть/быть forms ===
    "суть", "есмь", "еси", "будь", "будьте",
    # === Missing prepositions ===
    "без", "безо",
    # === Possessives without ё (corpus often writes е for ё) ===
    "твое", "твоем", "свое", "своем", "мое", "моем",
    # === Additional demonstratives/pronouns ===
    "том", "всю", "весе",
    # === Pre-reform pronoun forms ===
    "ея", "оне",
    # === Adverbial/discourse ===
    "отколь", "откуда", "доколь", "доколе",
    "напротив", "сейчас", "весьма",
    "некоторые", "некоторых", "некоторым",
    "рядом", "наконец",
    # === Bibliographic abbreviations ===
    "стр", "рис",
    # === Misc function words ===
    "оно", "каждый", "каждая", "каждое", "каждого",
    "весь", "вся", "все", "всё", "всего", "всей", "всех", "всем", "всему",
    "иной", "иная", "иное", "иного", "иной", "иных", "иным",
    "некий", "некая", "некое", "некого", "некоего",
    "сколько", "столько", "несколько",
    "оба", "обе", "обоих", "обеих",
    "тогда", "потом", "затем",
    "почти", "совсем", "вполне",
    "довольно", "слишком", "очень",
    "отнюдь", "впрочем", "однако",
    "именно", "конечно",
    "пока", "покуда", "доколе",
    # === Verbal particles ===
    "бы", "б",
]


# ═══════════════════════════════════════════════════════════════════════════════
# DUTCH STOP WORDS (v4.8.16)
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4816_NL = [
    # === Pronouns (formal/archaic/reflexive) ===
    "gij", "ge", "uw", "uwe", "u",
    "men", "zelf", "zelfs", "zelve",
    "elkander", "elkaar", "mekaar",
    "beide", "beiden", "beider",
    "ieder", "iedere", "iedereen",
    "niemand", "iemand", "niets", "iets",
    "alles", "allen", "alle",
    "dezelfde", "hetzelfde",
    "degene", "degenen", "diegene",
    # === Adverbs/particles ===
    "af", "mee", "heen", "weg", "terug", "voort", "toe",
    "alleen", "even", "aldus", "alzo", "evenwel",
    "eensklaps", "plotseling", "opeens",
    "daarheen", "hierheen", "waarheen",
    "waarvan", "waardoor", "waarbij", "waarvoor",
    "waarop", "waartoe", "waarmede", "waarmee",
    "hiervan", "hiermee", "hiervoor", "hierover",
    "daarvan", "daarmede", "daarmee", "daarvoor", "daarover",
    "daaruit", "hieruit", "waaruit",
    "overal", "nergens", "ergens",
    "altijd", "nooit", "ooit",
    "dikwijls", "dikwerf", "menigmaal",
    "inmiddels", "ondertussen", "intussen",
    "thans", "destijds", "weleer", "voorheen",
    "weldra", "spoedig", "terstond",
    "eenmaal", "andermaal", "tweemaal",
    "soms", "wellicht", "misschien",
    "genoeg", "voldoende", "tamelijk", "vrij",
    "gaarne", "liever", "liefst",
    "immers", "namelijk", "trouwens",
    "daarom", "derhalve", "bijgevolg",
    "nochtans", "niettemin", "desondanks",
    "bovendien", "buitendien",
    # === Old Dutch forms ===
    "zoo", "zooals", "zooveel", "zoodanig", "zoodra",
    "dezer", "dezen", "dezes",
    "dier", "dies", "diens",
    "wier", "welker", "welks",
    "zulk", "zulke", "zulks",
    "alsdan", "alsmede", "alsmaar",
    # === Conjunctions ===
    "één", "mits", "tenzij", "ofschoon",
    "hoewel", "hoegenaamd", "hoezeer",
    "naarmate", "naargelang",
    "zodra", "zolang", "voordat", "nadat",
    "opdat", "doordat", "totdat",
    "behalve", "uitgezonderd",
    # === Exclamations ===
    "ach", "och", "helaas",
    # === Function words ===
    "per", "via", "circa", "omtrent", "circa",
    "betreffende", "aangaande", "omtrent",
    "gedurende", "tijdens", "sedert", "sinds",
    "jegens", "tegenover",
    "ondanks", "wegens",
    "middels", "dankzij",
]


# ═══════════════════════════════════════════════════════════════════════════════
# PROPER NOUNS (v4.8.16) — corpus-specific
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4816_RU = [
    # pg14741 — Derzhavin odes (biblical/historical)
    "державин", "ломоносов", "петров", "суворов",
    "давид", "моисей", "авраам", "иаков", "исаия",
    "иеремия", "иезекииль", "даниил",
    "пётр", "павел", "иоанн", "матфей",
    "иерусалим", "сион", "вавилон", "египет",
    "россия", "русь",
    # pg30774 — Foreign travelers in Muscovy
    "олеарий", "олеария", "олеарій",
    "герберштейн", "герберштейна",
    "корб", "корба",
    "московия", "московіи", "московія",
    "россия", "россіи", "россію",
    "москва", "москвы",
    "иван", "пётр", "борис", "годунов",
    "лжедмитрий",
    # pg16527 — Commercial/trade text
    "петербург", "новгород", "киев",
]

PROPER_NOUNS_V4816_NL = [
    # pg18066 — Columbus
    "columbus", "ferdinand", "isabella",
    "guacanagari", "ojeda", "diego", "bartholomeus",
    "vespucci", "bobadilla", "ovando", "roldan",
    "hispaniola", "cuba", "jamaica", "haiti",
    "san salvador", "trinidad", "porto rico",
    "genua", "lissabon", "cadiz", "palos",
    "spanje", "portugal", "engeland", "holland",
    "isabella", "ferdinando",
    # pg17525 — Buysse
    "vreught", "blink", "badoe", "soera",
    "bavel", "congoland",
    "buysse", "cyriel",
    "blikslager",
]


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_keywords_v4816() -> dict:
    """Return {lang: {atom: [words]}} for v4816 keywords."""
    merged = {}
    for lang, atoms in KEYWORDS_V4816_RU.items():
        merged[lang] = atoms
    for lang, atoms in KEYWORDS_V4816_NL.items():
        merged[lang] = atoms
    return merged


def get_stop_words_v4816() -> dict:
    """Return {lang: [words]} for v4816 stop words."""
    return {
        "ru": STOP_WORDS_V4816_RU,
        "nl": STOP_WORDS_V4816_NL,
    }


def get_proper_nouns_v4816() -> dict:
    """Return {lang: [names]} for v4816 proper nouns."""
    return {
        "ru": PROPER_NOUNS_V4816_RU,
        "nl": PROPER_NOUNS_V4816_NL,
    }


def get_old_dutch_forms_v4816() -> dict:
    """Return {old: modern} mapping of pre-1947 Dutch spelling."""
    return OLD_DUTCH_SPELLING
