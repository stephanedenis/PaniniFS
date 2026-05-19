#!/usr/bin/env python3
"""vocabulary_expansion_v4813.py — v4.8.13: Chinese vocabulary expansion

Root cause analysis of zh 33.8% coverage revealed:
 1. Traditional↔Simplified mismatch (fixed via OpenCC in pipeline)
 2. Missing stop words (fixed in STOP_WORDS["zh"])
 3. Missing zh content keywords for many common characters

This module provides:
 - ZH keyword mappings for 36 high-frequency characters → atoms
 - ZH proper nouns (surnames from the Four Great Classical Novels)
 - Additional ZH stop words (function words not in base set)

Corpus context: the zh Gutenberg files are the Four Classics (四大名著):
 - 紅樓夢 Dream of the Red Chamber (pg23839, pg23863)
 - 西遊記 Journey to the West (pg23950, pg23962)
 - 水滸傳 Water Margin (pg24264)
 - 三國演義 Romance of the Three Kingdoms (pg27166)
 - Plus smaller texts (pg23864, pg7337)

Created: 2026-02-22 by Copilot (Claude Opus 4.6) on hauru
"""

# ═══════════════════════════════════════════════════════════════════════════════
# ZH KEYWORDS — single-character content words mapped to atoms
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4813 = {
    # ── TEMPS (time) ──────────────────────────────────────────────────────────
    "EXISTENCE": {
        "zh": [
            "日",   # rì — day, sun, daily
            "时",   # shí — time, hour, when
            "年",   # nián — year
            "今",   # jīn — now, today, this (temporal)
            "夜",   # yè — night
            "早",   # zǎo — early, morning
            "晚",   # wǎn — late, evening
            "春",   # chūn — spring (season)
            "秋",   # qiū — autumn (season)
            "月",   # yuè — moon, month
        ],
    },

    # ── MOUVEMENT (movement, transport) ───────────────────────────────────────
    "MOUVEMENT": {
        "zh": [
            "马",   # mǎ — horse (mount, transport)
            "起",   # qǐ — rise, get up, start
            "引",   # yǐn — lead, guide, pull
            "飞",   # fēi — fly
            "追",   # zhuī — chase, pursue
            "逃",   # táo — escape, flee
            "跑",   # pǎo — run
            "送",   # sòng — send, deliver, escort
            "步",   # bù — step, walk, pace
            "落",   # luò — fall, drop
        ],
    },

    # ── PROCESSUS (action, doing) ─────────────────────────────────────────────
    "DESTRUCTION": {
        "zh": [
            "打",   # dǎ — hit, strike, beat
            "杀",   # shā — kill, slay
            "破",   # pò — break, destroy
            "伤",   # shāng — wound, injure
            "败",   # bài — defeat, lose
        ],
    },

    "CREATION": {
        "zh": [
            "做",   # zuò — do, make, produce
            "造",   # zào — create, build, manufacture
            "修",   # xiū — repair, cultivate, build
            "立",   # lì — establish, stand, erect
            "写",   # xiě — write
            "画",   # huà — draw, paint
        ],
    },

    "POSSESSION": {
        "zh": [
            "拿",   # ná — take, grab, hold
            "送",   # sòng — give, send
            "收",   # shōu — receive, collect, harvest
            "还",   # huán — return, give back
            "借",   # jiè — borrow, lend
            "买",   # mǎi — buy
            "卖",   # mài — sell
            "赏",   # shǎng — reward, bestow
            "带",   # dài — carry, bring, wear
        ],
    },

    # ── PERCEPTION & COGNITION ────────────────────────────────────────────────
    "PERCEPTION": {
        "zh": [
            "见",   # jiàn — see (already in keywords but ensure via expansion)
            "望",   # wàng — gaze, look into distance, hope
            "闻",   # wén — hear, smell, news
            "觉",   # jué — feel, sense, perceive
            "观",   # guān — observe, view, contemplate
        ],
    },

    "COGNITION": {
        "zh": [
            "想",   # xiǎng — think (already in keywords but ensure)
            "念",   # niàn — think of, recite, study
            "悟",   # wù — enlighten, realize, awaken
            "忘",   # wàng — forget
            "记",   # jì — remember, record
            "疑",   # yí — doubt, suspect
            "料",   # liào — expect, estimate, anticipate
            "算",   # suàn — calculate, reckon, consider
        ],
    },

    # ── COMMUNICATION (speech, language) ──────────────────────────────────────
    "COMMUNICATION": {
        "zh": [
            "教",   # jiào/jiāo — teach, instruct / make, cause
            "云",   # yún — say (classical), cloud
            "报",   # bào — report, announce, newspaper
            "叫",   # jiào — call, shout, name
            "问",   # wèn — ask, inquire
            "答",   # dá — answer, reply
            "告",   # gào — tell, announce, accuse
            "读",   # dú — read
            "唱",   # chàng — sing
            "令",   # lìng — order, command, decree
            "书",   # shū — book, write, letter
            "诗",   # shī — poem, poetry
        ],
    },

    # ── SOCIAL (kinship, hierarchy) ───────────────────────────────────────────
    "AGENT": {
        "zh": [
            "师",   # shī — master, teacher, army
            "僧",   # sēng — monk, Buddhist monk
            "弟",   # dì — younger brother, disciple
            "哥",   # gē — elder brother
            "姐",   # jiě — elder sister
            "娘",   # niáng — mother, lady, young woman
            "爷",   # yé — father, grandfather, lord
            "奶",   # nǎi — grandmother, madam, milk
            "兵",   # bīng — soldier, military
            "王",   # wáng — king
            "帝",   # dì — emperor
            "将",   # jiàng — general (military rank)
            "官",   # guān — official, officer
            "臣",   # chén — minister, subject
            "妻",   # qī — wife
            "夫",   # fū — husband, man
            "子",   # zǐ — child, son, master (honorific)
            "女",   # nǚ — woman, daughter, girl
            "贼",   # zéi — thief, bandit, rebel
        ],
    },

    # ── QUALITÉ (qualities, attributes) ───────────────────────────────────────
    "BON": {
        "zh": [
            "圣",   # shèng — holy, sage, sacred
            "贵",   # guì — noble, precious, expensive
            "美",   # měi — beautiful, good
            "善",   # shàn — good, virtuous, kind
            "忠",   # zhōng — loyal, faithful
            "贤",   # xián — virtuous, worthy, talented
        ],
    },

    "MAUVAIS": {
        "zh": [
            "妖",   # yāo — demon, supernatural, evil spirit
            "怪",   # guài — strange, monster, blame
            "恶",   # è — evil, wicked, fierce
            "贪",   # tān — greedy, corrupt
            "毒",   # dú — poison, toxic, cruel
            "假",   # jiǎ — false, fake
        ],
    },

    "GRAND": {
        "zh": [
            "高",   # gāo — tall, high
            "远",   # yuǎn — far, distant
            "深",   # shēn — deep, profound
            "广",   # guǎng — wide, broad, extensive
            "重",   # zhòng — heavy, important, serious
            "强",   # qiáng — strong, powerful
            "满",   # mǎn — full, filled, satisfied
        ],
    },

    "INTENSE": {
        "zh": [
            "忙",   # máng — busy, hurried, rush
            "急",   # jí — urgent, anxious, hurry
            "猛",   # měng — fierce, violent, suddenly
            "烈",   # liè — intense, ardent, fierce
            "勇",   # yǒng — brave, courageous
        ],
    },

    # ── POSITION (space, location) ────────────────────────────────────────────
    "LIEU": {
        "zh": [
            "住",   # zhù — live, reside, stay, stop
            "坐",   # zuò — sit, seat, ride
            "寨",   # zhài — stronghold, camp, stockade
            "州",   # zhōu — state, province, prefecture
            "城",   # chéng — city, wall, town
            "山",   # shān — mountain, hill
            "河",   # hé — river
            "桥",   # qiáo — bridge
            "路",   # lù — road, path, way
            "门",   # mén — door, gate, entrance
            "房",   # fáng — room, house
            "庄",   # zhuāng — manor, village, solemn
            "庙",   # miào — temple, shrine
            "林",   # lín — forest, grove
            "园",   # yuán — garden, park
            "宫",   # gōng — palace, temple
            "洞",   # dòng — cave, hole
            "营",   # yíng — camp, barracks, manage
        ],
    },

    # ── MATIÈRE (substance, material) ─────────────────────────────────────────
    "MATIÈRE": {
        "zh": [
            "酒",   # jiǔ — wine, alcohol, liquor
            "饭",   # fàn — rice, meal, food
            "肉",   # ròu — meat, flesh
            "药",   # yào — medicine, drug
            "衣",   # yī — clothing, garment
            "刀",   # dāo — knife, sword, blade
            "枪",   # qiāng — spear, gun, lance
            "宝",   # bǎo — treasure, precious, jewel
            "金",   # jīn — gold, metal, money
            "铁",   # tiě — iron
            "石",   # shí — stone, rock
            "船",   # chuán — ship, boat
            "车",   # chē — cart, vehicle, car
        ],
    },

    # ── CORPS (body) ──────────────────────────────────────────────────────────
    "CORPS": {
        "zh": [
            "头",   # tóu — head, top, first
            "手",   # shǒu — hand
            "身",   # shēn — body, self, life
            "脸",   # liǎn — face
            "眼",   # yǎn — eye
            "口",   # kǒu — mouth, opening
            "心",   # xīn — heart (already in keywords, reinforce)
            "血",   # xuè — blood
            "骨",   # gǔ — bone
        ],
    },

    # ── EMOTIONS ──────────────────────────────────────────────────────────────
    "FEAR": {
        "zh": [
            "惊",   # jīng — startle, frighten, alarm
            "慌",   # huāng — panic, flustered
        ],
    },

    "GRIEF": {
        "zh": [
            "哭",   # kū — cry, weep
            "泪",   # lèi — tears
            "悲",   # bēi — sad, sorrowful
            "苦",   # kǔ — bitter, suffering
        ],
    },

    "RAGE": {
        "zh": [
            "怒",   # nù — anger, fury (reinforce)
            "骂",   # mà — scold, curse
        ],
    },

    "PLAY": {
        "zh": [
            "笑",   # xiào — laugh, smile (reinforce)
            "乐",   # lè — joy, happy, music
            "欢",   # huān — merry, joyful, pleased
            "喜",   # xǐ — happy, pleased, like
        ],
    },

    # ── PROCESSUS (general actions) ───────────────────────────────────────────
    "SEEKING": {
        "zh": [
            "寻",   # xún — seek, search
            "找",   # zhǎo — look for, find
            "求",   # qiú — beg, request, seek
            "探",   # tàn — explore, spy, probe
        ],
    },

    "DOMINATION": {
        "zh": [
            "使",   # shǐ — use, make, cause, envoy
            "令",   # lìng — order, command, decree
            "治",   # zhì — govern, cure, manage
            "管",   # guǎn — manage, control, pipe
            "守",   # shǒu — guard, defend, keep
            "保",   # bǎo — protect, guarantee
            "攻",   # gōng — attack, assault
            "战",   # zhàn — fight, battle, war
        ],
    },

    "CARE": {
        "zh": [
            "救",   # jiù — save, rescue, help
            "医",   # yī — doctor, medicine, heal
            "养",   # yǎng — raise, nourish, support
            "敬",   # jìng — respect, revere
            "爱",   # ài — love (reinforce)
            "怜",   # lián — pity, compassion
        ],
    },

    # ── RELATION (connection, association) ────────────────────────────────────
    "RELATION": {
        "zh": [
            "合",   # hé — combine, together, join
            "分",   # fēn — divide, separate, share
            "连",   # lián — connect, link, continuous
            "交",   # jiāo — exchange, hand over, intersect
            "离",   # lí — leave, separate, from
            "配",   # pèi — match, pair, distribute
        ],
    },

    # ── STRUCTURE (form, organization) ────────────────────────────────────────
    "STRUCTURE": {
        "zh": [
            "阵",   # zhèn — battle formation, array
            "法",   # fǎ — law, method, way
            "术",   # shù — technique, skill, art
            "计",   # jì — plan, strategy, count
            "策",   # cè — plan, scheme, policy
        ],
    },

    # ── EXISTENCE (being, identity) ───────────────────────────────────────────
    "VRAI": {
        "zh": [
            "真",   # zhēn — true, genuine, real (reinforce)
            "实",   # shí — real, solid, honest
            "正",   # zhèng — correct, upright, exactly
            "明",   # míng — bright, clear, wise, Ming dynasty
            "信",   # xìn — believe, trust, letter
        ],
    },

    # ── MESURE (quantity, evaluation) ─────────────────────────────────────────
    "MESURE": {
        "zh": [
            "长",   # cháng/zhǎng — long, grow, elder
            "短",   # duǎn — short, brief
            "少",   # shǎo — few, little, young
            "尽",   # jìn — exhaust, completely, all
            "足",   # zú — enough, foot, sufficient
        ],
    },

    # ── RÉCURRENCE (repetition, cycle) ────────────────────────────────────────
    "RÉCURRENCE": {
        "zh": [
            "常",   # cháng — often, normal, constant
            "再",   # zài — again, once more (reinforce)
            "复",   # fù — repeat, return, recover
            "续",   # xù — continue, extend
        ],
    },

    # ── ORDRE (order, arrangement) ────────────────────────────────────────────
    "ORDRE": {
        "zh": [
            "先",   # xiān — first, before, ahead
            "次",   # cì — next, time (ordinal), secondary
            "初",   # chū — beginning, first, initial
            "终",   # zhōng — end, final, eventually
        ],
    },

    # ── DUALITÉ (opposition, contrast) ────────────────────────────────────────
    "DUALITÉ": {
        "zh": [
            "阴",   # yīn — yin, shadow, negative
            "阳",   # yáng — yang, sun, positive
            "黑",   # hēi — black, dark
            "白",   # bái — white, clear, plain
            "生",   # shēng — life, birth, raw
            "死",   # sǐ — death, die, dead
        ],
    },

    # ── INVARIANCE (stability, permanence) ────────────────────────────────────
    "INVARIANCE": {
        "zh": [
            "定",   # dìng — fixed, certain, decide
            "稳",   # wěn — stable, steady
            "永",   # yǒng — eternal, forever
            "固",   # gù — solid, firm, stubborn
        ],
    },

    # ── QUAL (quality, nature) ────────────────────────────────────────────────
    "QUAL": {
        "zh": [
            "色",   # sè — color, appearance, lust
            "味",   # wèi — taste, flavor, smell
            "声",   # shēng — sound, voice, reputation
            "香",   # xiāng — fragrant, incense, delicious
            "暗",   # àn — dark, dim, hidden
            "亮",   # liàng — bright, light, clear
            "冷",   # lěng — cold, cool
            "热",   # rè — hot, warm, popular
            "干",   # gān — dry, clean, do
            "湿",   # shī — wet, damp, humid
        ],
    },

    # ── QUALITÉ ───────────────────────────────────────────────────────────────
    "QUALITÉ": {
        "zh": [
            "好",   # hǎo — good, well, fine (reinforce)
            "坏",   # huài — bad, broken, spoiled
            "新",   # xīn — new, fresh
            "旧",   # jiù — old, former, used
            "快",   # kuài — fast, quick, happy
            "慢",   # màn — slow, leisurely
            "难",   # nán — difficult, hard, disaster
            "易",   # yì — easy, change
        ],
    },

    # ── ANCIENT (old, classical) ──────────────────────────────────────────────
    "ANCIEN": {
        "zh": [
            "古",   # gǔ — ancient, old
            "老",   # lǎo — old, experienced, always
            "祖",   # zǔ — ancestor, grandfather
        ],
    },

    # ── DISGUST ───────────────────────────────────────────────────────────────
    "DISGUST": {
        "zh": [
            "脏",   # zāng — dirty, filthy
            "臭",   # chòu — stinky, smelly, bad
            "厌",   # yàn — weary of, dislike
        ],
    },

    # ── TEDIUM ────────────────────────────────────────────────────────────────
    "TEDIUM": {
        "zh": [
            "闲",   # xián — idle, leisure, free
            "倦",   # juàn — tired, weary
            "烦",   # fán — annoyed, vexed, trouble
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ZH KEYWORDS — WAVE 2: high-frequency characters still uncovered after Wave 1
# Top 80 uncovered analysis on 8 zh files (1.6M content words, 60.1% → ?)
# ═══════════════════════════════════════════════════════════════════════════════

_KEYWORDS_WAVE2 = {
    # ── MESURE ────────────────────────────────────────────────────────────────
    "MESURE": {
        "zh": [
            "小",   # xiǎo — small, little, young
            "点",   # diǎn — dot, point, a little, o'clock
            "朝",   # cháo/zhāo — dynasty, court / morning
        ],
    },

    # ── MOUVEMENT ─────────────────────────────────────────────────────────────
    "MOUVEMENT": {
        "zh": [
            "开",   # kāi — open, start, drive
            "放",   # fàng — release, put, let go
            "赶",   # gǎn — hurry, chase, drive away
            "回",   # huí — return, turn back (reinforce in content context)
        ],
    },

    # ── DESTRUCTION ───────────────────────────────────────────────────────────
    "DESTRUCTION": {
        "zh": [
            "乱",   # luàn — chaos, disorder, confused
        ],
    },

    # ── CREATION ──────────────────────────────────────────────────────────────
    "CREATION": {
        "zh": [
            "变",   # biàn — change, transform, become
        ],
    },

    # ── PERCEPTION ────────────────────────────────────────────────────────────
    "PERCEPTION": {
        "zh": [
            "受",   # shòu — receive, endure, suffer
        ],
    },

    # ── COGNITION ─────────────────────────────────────────────────────────────
    "COGNITION": {
        "zh": [
            "神",   # shén — spirit, god, divine, supernatural
            "经",   # jīng — sutra, classic, pass through
            "精",   # jīng — essence, spirit, refined, demon
        ],
    },

    # ── COMMUNICATION ─────────────────────────────────────────────────────────
    "COMMUNICATION": {
        "zh": [
            "名",   # míng — name, fame, title
            "文",   # wén — writing, literature, culture
            "字",   # zì — character, word, letter, name
            "迎",   # yíng — welcome, greet, meet
            "唤",   # huàn — call, summon, wake up
        ],
    },

    # ── AGENT ─────────────────────────────────────────────────────────────────
    "AGENT": {
        "zh": [
            "士",   # shì — scholar, warrior, gentleman
            "婆",   # pó — old woman, mother-in-law, granny
            "汉",   # hàn — Han Chinese, man, fellow
        ],
    },

    # ── RELATION ──────────────────────────────────────────────────────────────
    "RELATION": {
        "zh": [
            "兄",   # xiōng — elder brother
            "姑",   # gū — aunt (paternal), mother-in-law
            "妹",   # mèi — younger sister
            "拜",   # bài — bow, worship, pay respects, visit
            "接",   # jiē — receive, connect, welcome, catch
        ],
    },

    # ── DOMINATION ────────────────────────────────────────────────────────────
    "DOMINATION": {
        "zh": [
            "敢",   # gǎn — dare, venture, bold
            "领",   # lǐng — lead, command, collar, receive
            "胜",   # shèng — victory, surpass, superior
        ],
    },

    # ── LIEU ──────────────────────────────────────────────────────────────────
    "LIEU": {
        "zh": [
            "府",   # fǔ — mansion, prefecture, government office
        ],
    },

    # ── MATIÈRE ───────────────────────────────────────────────────────────────
    "MATIÈRE": {
        "zh": [
            "风",   # fēng — wind, style, custom
            "花",   # huā — flower, blossom, spend
        ],
    },

    # ── CORPS ─────────────────────────────────────────────────────────────────
    "CORPS": {
        "zh": [
            "吃",   # chī — eat, consume, suffer
            "喝",   # hē — drink / hè — shout
        ],
    },

    # ── INVARIANCE ────────────────────────────────────────────────────────────
    "INVARIANCE": {
        "zh": [
            "平",   # píng — flat, peaceful, equal, ordinary
            "留",   # liú — stay, remain, keep, leave behind
            "休",   # xiū — rest, stop, cease, don't
        ],
    },

    # ── QUAL ──────────────────────────────────────────────────────────────────
    "QUAL": {
        "zh": [
            "红",   # hóng — red (Dream of the Red Chamber!)
        ],
    },

    # ── EXISTENCE ─────────────────────────────────────────────────────────────
    "EXISTENCE": {
        "zh": [
            "性",   # xìng — nature, character, sex, temperament
        ],
    },

    # ── ORDRE ─────────────────────────────────────────────────────────────────
    "ORDRE": {
        "zh": [
            "礼",   # lǐ — ritual, courtesy, propriety, gift
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ZH KEYWORDS — WAVE 3: chars #31-100 from uncovered analysis (68.4% → ?)
# Diminishing returns zone: each char ~700-1050 occurrences
# ═══════════════════════════════════════════════════════════════════════════════

_KEYWORDS_WAVE3 = {
    "MOUVEMENT": {
        "zh": [
            "冲",   # chōng — rush, charge, rinse
            "转",   # zhuǎn — turn, revolve, transfer
            "投",   # tóu — throw, submit, join
            "散",   # sàn — scatter, disperse, break up
            "奔",   # bēn — run, rush, flee
            "流",   # liú — flow, stream, drift
            "穿",   # chuān — wear, pass through, pierce
            "举",   # jǔ — lift, raise, elect, act
            "弄",   # nòng — play with, handle, do
            "延",   # yán — extend, delay, invite
            "提",   # tí — lift, mention, carry, raise
        ],
    },

    "COMMUNICATION": {
        "zh": [
            "谢",   # xiè — thank, decline, wither
            "传",   # chuán — transmit, pass on, biography
            "议",   # yì — discuss, propose, opinion
            "姓",   # xìng — surname, family name
            "句",   # jù — sentence, phrase, line
            "奏",   # zòu — play music, present to emperor
            "劝",   # quàn — advise, persuade, encourage
            "称",   # chēng — call, name, weigh, claim
            "商",   # shāng — discuss, trade, merchant
        ],
    },

    "AGENT": {
        "zh": [
            "丫",   # yā — servant girl (丫头 yātou), fork
            "妈",   # mā — mother, ma
            "客",   # kè — guest, visitor, traveler
            "徒",   # tú — disciple, follower, on foot
        ],
    },

    "COGNITION": {
        "zh": [
            "佛",   # fó — Buddha, Buddhism
            "认",   # rèn — recognize, acknowledge, admit
            "灵",   # líng — spirit, clever, effective, soul
        ],
    },

    "QUAL": {
        "zh": [
            "细",   # xì — fine, thin, detailed, careful
            "青",   # qīng — green, blue, young, black
            "轻",   # qīng — light (weight), gentle, young
            "容",   # róng — appearance, tolerate, contain
            "紫",   # zǐ — purple, violet
        ],
    },

    "DOMINATION": {
        "zh": [
            "功",   # gōng — merit, achievement, skill
            "奉",   # fèng — serve, present, obey orders
            "敌",   # dí — enemy, oppose, rival
            "势",   # shì — power, force, momentum
        ],
    },

    "CORPS": {
        "zh": [
            "病",   # bìng — sick, illness, disease
            "睡",   # shuì — sleep
            "脚",   # jiǎo — foot, leg, base
        ],
    },

    "MAUVAIS": {
        "zh": [
            "罪",   # zuì — crime, guilt, sin, blame
            "魔",   # mó — demon, devil, magic
        ],
    },

    "DESTRUCTION": {
        "zh": [
            "害",   # hài — harm, injure, kill, evil
        ],
    },

    "CREATION": {
        "zh": [
            "化",   # huà — transform, change, -ize
        ],
    },

    "MATIÈRE": {
        "zh": [
            "虎",   # hǔ — tiger
            "棒",   # bàng — stick, club, rod, great
            "草",   # cǎo — grass, herb, straw, draft
            "茶",   # chá — tea
            "雨",   # yǔ — rain
            "星",   # xīng — star, celestial body
        ],
    },

    "INTENSE": {
        "zh": [
            "力",   # lì — strength, power, force
        ],
    },

    "EXISTENCE": {
        "zh": [
            "世",   # shì — world, era, generation
        ],
    },

    "RELATION": {
        "zh": [
            "通",   # tōng — through, connect, communicate
            "叔",   # shū — uncle (father's younger brother)
            "姨",   # yí — aunt (maternal), concubine
        ],
    },

    "MESURE": {
        "zh": [
            "久",   # jiǔ — long time, long-lasting
            "差",   # chā/chà — difference, send, poor
        ],
    },

    "INVARIANCE": {
        "zh": [
            "歇",   # xiē — rest, stop, take a break
            "顺",   # shùn — smooth, obey, along
        ],
    },

    "LIEU": {
        "zh": [
            "县",   # xiàn — county, district
            "村",   # cūn — village
            "屋",   # wū — room, house, building
        ],
    },

    "TEDIUM": {
        "zh": [
            "呆",   # dāi — dull, stupid, dazed, blank
        ],
    },

    "POSSESSION": {
        "zh": [
            "包",   # bāo — wrap, package, include
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# WAVE 3: Additional proper nouns
# ═══════════════════════════════════════════════════════════════════════════════

_PROPER_NOUNS_WAVE3 = {
    "zh": [
        "钗",   # Chāi — Xue Baochai 薛宝钗 (hairpin)
        "政",   # Zhèng — Jia Zheng 贾政 (government)
        "琏",   # Liǎn — Jia Lian 贾琏
        "侯",   # Hóu — title Marquis / surname
        "宗",   # Zōng — surname / ancestor clan
        "盖",   # Gài — surname (Water Margin)
        "蜀",   # Shǔ — Shu state 蜀国 (Three Kingdoms)
        "菩",   # Pú — first char of 菩萨 Bodhisattva
        "萨",   # Sà — second char of 菩萨
        "史",   # Shǐ — surname (Dream) / history
        "梁",   # Liáng — Liangshan 梁山泊 (Water Margin)
        "朱",   # Zhū — Zhu surname
        "顾",   # Gù — Gu surname
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# WAVE 3: Additional stop words
# ═══════════════════════════════════════════════════════════════════════════════

_STOP_WORDS_WAVE3 = {
    "zh": [
        "the",  # English word leak in zh Gutenberg texts
        "of",   # English word leak
        "莫",   # mò — don't, no one (classical negation)
        "位",   # wèi — classifier for people (measure word)
        "余",   # yú — I/me (classical pronoun) / remainder
        "厮",   # sī — fellow, each other (classical)
        "毕",   # bì — finish, after all (毕竟)
        "须",   # xū — must, need, beard
        "肯",   # kěn — willing, agree
        "依",   # yī — according to, rely on
        "右",   # yòu — right (direction)
        "竟",   # jìng — unexpectedly, actually
        "条",   # tiáo — classifier (measure word for long things)
        "候",   # hòu — wait, time (时候 shíhou)
        "岂",   # qǐ — how could? (classical rhetorical)
        "乎",   # hū — particle (classical, 于乎)
        "该",   # gāi — should, this (modal)
        "哩",   # li — particle (dialectal sentence-final)
        "跟",   # gēn — with, follow (preposition)
        "氏",   # shì — clan, family (suffix, 诸葛氏)
        "兴",   # xìng — mood, interest / xīng — prosper
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ZH PROPER NOUNS — Surnames & character names from the Four Classics
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4813 = {
    "zh": [
        # ── Surnames (appear as single characters in classical Chinese) ───────
        "贾",   # Jiǎ — Dream of Red Chamber
        "张",   # Zhāng
        "孙",   # Sūn — Sun Wukong
        "曹",   # Cáo — Cao Cao
        "李",   # Lǐ
        "凤",   # Fèng — Wang Xifeng
        "孔",   # Kǒng — Kong Ming / Confucius
        "宋",   # Sòng — Song Jiang
        "林",   # Lín — Lin Daiyu / Lin Chong
        "刘",   # Liú — Liu Bei
        "赵",   # Zhào — Zhao Yun
        "吕",   # Lǚ — Lü Bu
        "周",   # Zhōu — Zhou Yu
        "袁",   # Yuán — Yuan Shao
        "诸",   # Zhū — Zhuge (first char of 诸葛)
        "黄",   # Huáng — Huang Zhong
        "许",   # Xǔ — Xu Chu
        "薛",   # Xuē — Xue Baochai family
        "王",   # Wáng — (can also mean king)
        "陈",   # Chén
        "杨",   # Yáng
        "唐",   # Táng — Tang Sanzang / Tang dynasty
        "鲁",   # Lǔ — Lu Zhishen / Lu Su
        "燕",   # Yān — Yan (place/surname)
        "秦",   # Qín — Qin (surname/dynasty)
        "潘",   # Pān — Pan Jinlian
        "吴",   # Wú — Wu (kingdom/surname)
        "高",   # Gāo — Gao Qiu (also = tall)
        "韩",   # Hán
        "董",   # Dǒng — Dong Zhuo
        "袭",   # Xí — Xiren (Dream)
        # ── Wave 2: given names & state names from Four Classics ──────────────
        "操",   # Cāo — Cao Cao 曹操 (also = conduct/drill)
        "玄",   # Xuán — Xuanzang 玄奘 / Liu Xuande 刘玄德
        "武",   # Wǔ — Wu Song 武松, martial
        "戒",   # Jiè — Bajie 八戒 (Eight Precepts)
        "藏",   # Zàng — Sanzang 三藏 (Tripitaka)
        "关",   # Guān — Guan Yu 关羽 (also = pass/barrier)
        "龙",   # Lóng — White Dragon Horse 白龙马
        "黛",   # Dài — Lin Daiyu 林黛玉
        "魏",   # Wèi — Wei kingdom 魏国
        "备",   # Bèi — Liu Bei 刘备 (also = prepare)
        "齐",   # Qí — Qi state 齐国
        "松",   # Sōng — Wu Song 武松 (also = pine tree)
        "江",   # Jiāng — Song Jiang 宋江 (also = river)
        "安",   # Ān — various chars (also = peace/safe)
        "沙",   # Shā — Sha Wujing 沙悟净 (also = sand)
        "司",   # Sī — Sima 司马 (also = department)
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ZH STOP WORDS — Additional function words for classical Chinese
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4813 = {
    "zh": [
        # Interrogatives (as single chars in classical text)
        "什",   # shén (什么 = what)
        "怎",   # zěn (怎么 = how)
        "几",   # jǐ (how many)
        # Classical function words
        "乃",   # nǎi — classical copula (is/therefore)
        "皆",   # jiē — all (classical adverb)
        "甲",   # jiǎ — first (ordinal, like 甲乙)
        "乙",   # yǐ — second (ordinal)
        # Adverbs / degree words
        "多",   # duō — many, much, more (degree)
        "样",   # yàng — manner (这样 = like this)
        # Locative suffixes
        "边",   # biān — side (旁边, 外边)
        # Classical pronoun
        "吾",   # wú — I/me (classical 1st person)
        # Sentence particles
        "罢",   # ba/bà — (sentence-final particle, stop)
        # Direction/position as function
        "东",   # dōng — east
        "西",   # xī — west
        "南",   # nán — south
        "北",   # běi — north
        # Common suffixes acting as grammatical markers
        "们",   # men — plural marker (if not already in base)
        "般",   # bān — sort, kind (如此般)
        "处",   # chù — place (suffix)
        # ── Wave 2: additional function words from top-80 uncovered ───────────
        "当",   # dāng — when, should, act as (modal/temporal)
        "请",   # qǐng — please, invite (polite marker)
        "即",   # jí — then, immediately, is (classical copula)
        "各",   # gè — each, every
        "别",   # bié — don't, other, separate
        "应",   # yīng — should, ought to, answer
        "本",   # běn — this, originally, root
        "并",   # bìng — and, moreover, actually
        "忽",   # hū — suddenly, neglect
        "虽",   # suī — although, even though
        "直",   # zhí — directly, straight, continuously
        "遂",   # suì — thereupon, then (classical narrative)
        "向",   # xiàng — toward, facing, previous
        "随",   # suí — follow, along, let, as
        "既",   # jì — since, already, both...and
        "非",   # fēi — not, wrong, un- (negation)
        "似",   # sì — seem, like, as if
        "汝",   # rǔ — you, thou (classical 2nd person)
        "矣",   # yǐ — (classical sentence-final particle, perfective)
        "己",   # jǐ — self, oneself
        "左",   # zuǒ — left (direction/position)
        "曾",   # céng — once, ever, formerly (aspect)
        "尚",   # shàng — still, yet, even (adverb)
        "过",   # guò — (aspect particle: experiential, excess)
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ACCESSORS
# ═══════════════════════════════════════════════════════════════════════════════

def get_keywords_v4813():
    """Return merged Wave 1 + Wave 2 + Wave 3 keywords."""
    import copy
    merged = copy.deepcopy(KEYWORDS_V4813)
    for wave in (_KEYWORDS_WAVE2, _KEYWORDS_WAVE3):
        for atom, lang_words in wave.items():
            if atom in merged:
                for lang, words in lang_words.items():
                    existing = merged[atom].get(lang, [])
                    merged[atom][lang] = existing + words
            else:
                merged[atom] = dict(lang_words)
    return merged

def get_stop_words_v4813():
    """Return merged Wave 1 + Wave 3 stop words."""
    merged = {}
    for lang, words in STOP_WORDS_V4813.items():
        merged[lang] = list(words)
    for lang, words in _STOP_WORDS_WAVE3.items():
        merged.setdefault(lang, []).extend(words)
    return merged

def get_proper_nouns_v4813():
    """Return merged Wave 1 + Wave 3 proper nouns."""
    merged = {}
    for lang, names in PROPER_NOUNS_V4813.items():
        merged[lang] = list(names)
    for lang, names in _PROPER_NOUNS_WAVE3.items():
        merged.setdefault(lang, []).extend(names)
    return merged


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    merged_kw = get_keywords_v4813()
    merged_sw = get_stop_words_v4813()
    merged_pn = get_proper_nouns_v4813()

    kw = sum(len(ws) for atom in merged_kw.values() for ws in atom.values())
    kw_w1 = sum(len(ws) for atom in KEYWORDS_V4813.values() for ws in atom.values())
    kw_w2 = sum(len(ws) for atom in _KEYWORDS_WAVE2.values() for ws in atom.values())
    kw_w3 = sum(len(ws) for atom in _KEYWORDS_WAVE3.values() for ws in atom.values())
    sw = sum(len(ws) for ws in merged_sw.values())
    pn = sum(len(ns) for ns in merged_pn.values())
    total = kw + sw + pn

    print(f"v4.8.13 Vocabulary Expansion (Chinese / CJK):")
    print(f"  Keywords W1:  {kw_w1:>4} across {len(KEYWORDS_V4813)} atoms")
    print(f"  Keywords W2:  {kw_w2:>4} across {len(_KEYWORDS_WAVE2)} atoms")
    print(f"  Keywords W3:  {kw_w3:>4} across {len(_KEYWORDS_WAVE3)} atoms")
    print(f"  Keywords tot: {kw:>4} across {len(merged_kw)} atoms")
    print(f"  Stop words:   {sw:>4}")
    print(f"  Proper nouns: {pn:>4}")
    print(f"  ─────────────────")
    print(f"  Total:        {total:>4}")
    print()
    print("Atoms covered (merged):")
    for atom, langs in sorted(merged_kw.items()):
        zh_count = len(langs.get("zh", []))
        print(f"  {atom:<16} {zh_count:>3} zh")
