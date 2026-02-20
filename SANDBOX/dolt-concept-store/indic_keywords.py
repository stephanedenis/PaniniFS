#!/usr/bin/env python3
"""indic_keywords.py — Hindi (hi) & Sanskrit (sa) keyword extensions for PaniniFS.

Adds keyword sets for all 34 semantic atoms in Hindi (Devanagari) and
Sanskrit (both Devanagari and ITRANS romanization).

Named in honor of Pāṇini (पाणिनि, ~4th century BCE), the great Indian
grammarian whose Aṣṭādhyāyī formalized Sanskrit grammar with ~4000 sūtras —
the first formal system in the history of linguistics, and the inspiration
for PaniniFS itself.

Part of PaniniFS v4.4 — Indic language support.

Design notes:
  - hi keywords use standard Hindi (Devanagari script, खड़ी बोली)
  - sa keywords include BOTH Devanagari AND ITRANS romanization because
    Gutenberg's only Sanskrit text (pg9000, Vishnu Sahasranaamam) uses ITRANS
  - Devanagari uses spaces between words → standard whitespace tokenization works
  - Devanagari has no uppercase/lowercase → has_latin guard already handles this
  - Sanskrit dhatu (verbal roots) are included alongside inflected forms
  - Hindi vocabulary draws from Tatsama (Sanskrit-origin) and Tadbhava (evolved)
"""

INDIC_KEYWORDS = {
    # ═══════════════════════════════════════════════════════════════════
    # PROC atoms — predicative (actions, events)
    # ═══════════════════════════════════════════════════════════════════
    "MOUVEMENT": {
        "hi": ["चलना", "जाना", "आना", "दौड़ना", "उड़ना", "कूदना", "गिरना",
               "भागना", "चलना", "तैरना", "पहुँचना", "निकलना", "लौटना",
               "उतरना", "चढ़ना", "घूमना", "भटकना", "यात्रा", "गति", "मार्ग"],
        "sa": ["गम्", "गच्छति", "चल्", "चलति", "आगम्", "आगच्छति",
               "धाव्", "धावति", "पत्", "पतति", "प्लु", "प्लवते",
               "गति", "मार्ग", "पथ", "यात्रा", "प्रस्थान",
               # ITRANS for pg9000
               "gam", "gachChati", "chal", "chalati", "aagam",
               "dhaav", "pat", "patati", "gati", "maarga", "patha"],
    },
    "COGNITION": {
        "hi": ["सोचना", "जानना", "समझना", "विश्वास", "याद", "विचार",
               "बुद्धि", "ज्ञान", "मन", "चिंतन", "मानना", "सीखना",
               "पहचानना", "अनुमान", "तर्क", "मति", "बोध", "चेतना"],
        "sa": ["मन्", "मनुते", "ज्ञा", "जानाति", "बुध्", "बोधति",
               "चिन्त्", "चिन्तयति", "विद्", "वेत्ति", "स्मृ", "स्मरति",
               "ज्ञान", "बुद्धि", "मनस्", "विद्या", "प्रज्ञा", "मेधा",
               "man", "manute", "j~naa", "jaanaati", "budh", "bodhati",
               "chint", "chintayati", "vid", "vetti", "smR", "smarati",
               "j~naana", "buddhi", "manas", "vidyaa", "praj~naa"],
    },
    "PERCEPTION": {
        "hi": ["देखना", "सुनना", "छूना", "सूँघना", "चखना", "दृष्टि",
               "नज़र", "आँख", "कान", "स्पर्श", "अनुभव", "महसूस",
               "दिखना", "ध्वनि", "प्रकाश", "गंध", "रूप", "दर्शन"],
        "sa": ["दृश्", "पश्यति", "श्रु", "शृणोति", "स्पृश्", "स्पृशति",
               "घ्रा", "जिघ्रति", "रस्", "रसति", "नेत्र", "चक्षुस्",
               "कर्ण", "श्रवण", "दर्शन", "दृष्टि", "रूप", "ध्वनि",
               "dRsh", "pashyati", "shru", "shRNoti", "spRsh",
               "netra", "chakShus", "karNa", "darshana", "dRShTi", "ruupa"],
    },
    "COMMUNICATION": {
        "hi": ["बोलना", "कहना", "पूछना", "उत्तर", "पुकारना", "चिल्लाना",
               "बताना", "शब्द", "आवाज़", "भाषा", "वचन", "बात",
               "सुनाना", "घोषणा", "प्रश्न", "संवाद", "कथा", "गीत"],
        "sa": ["वद्", "वदति", "भाष्", "भाषते", "ब्रू", "ब्रवीति",
               "वच्", "वक्ति", "गै", "गायति", "शब्द", "वाक्",
               "वाणी", "वचन", "उक्ति", "भाषा", "कथा", "गीत",
               "vad", "vadati", "bhaaSh", "bhaaShate", "bruu", "braviiti",
               "vach", "vakti", "gai", "gaayati", "shabda", "vaak",
               "vaaNii", "vachana", "ukti"],
    },
    "CREATION": {
        "hi": ["बनाना", "रचना", "निर्माण", "लिखना", "उगाना", "काम",
               "सृष्टि", "कला", "शिल्प", "जन्म", "उत्पन्न", "बोना",
               "ढालना", "गढ़ना", "बुनना", "खेती", "कारीगर", "विकास"],
        "sa": ["कृ", "करोति", "सृज्", "सृजति", "रच्", "रचयति",
               "निर्मा", "निर्माति", "जन्", "जनयति", "सृष्टि", "रचना",
               "कर्मन्", "शिल्प", "कला", "निर्माण", "उत्पत्ति",
               "kR", "karoti", "sRj", "sRjati", "rach", "rachayati",
               "nirmaa", "jan", "janayati", "sRShTi", "karma", "shilpa"],
    },
    "EXISTENCE": {
        "hi": ["होना", "रहना", "जीना", "मरना", "जीवन", "मृत्यु",
               "अस्तित्व", "सत्य", "वास्तविक", "जन्म", "मौत",
               "प्राण", "आत्मा", "संसार", "लोक", "भव", "जगत"],
        "sa": ["अस्", "अस्ति", "भू", "भवति", "जीव्", "जीवति",
               "मृ", "म्रियते", "सत्", "असत्", "भव", "अभाव",
               "जीवन", "मृत्यु", "आत्मन्", "प्राण", "सत्य", "ब्रह्मन्",
               "as", "asti", "bhuu", "bhavati", "jiiv", "jiivati",
               "mR", "mriyate", "sat", "asat", "bhava", "abhaava",
               "jiivana", "mRtyu", "aatman", "praaNa", "satya", "brahman"],
    },
    "DESTRUCTION": {
        "hi": ["मारना", "तोड़ना", "नष्ट", "युद्ध", "लड़ाई", "हमला",
               "जलाना", "काटना", "विनाश", "संहार", "हिंसा", "सेना",
               "शस्त्र", "वध", "पराजय", "आक्रमण", "ध्वंस", "तलवार"],
        "sa": ["हन्", "हन्ति", "भिद्", "भिनत्ति", "छिद्", "छिनत्ति",
               "दह्", "दहति", "नश्", "नश्यति", "युद्ध", "संग्राम",
               "विनाश", "संहार", "शस्त्र", "खड्ग", "वध", "मृत्यु",
               "han", "hanti", "bhid", "Chid", "Chinatti",
               "dah", "dahati", "nash", "nashyati", "yuddha", "sangraama",
               "vinaasha", "samhaara", "shastra", "khaDga", "vadha"],
    },
    "POSSESSION": {
        "hi": ["रखना", "पाना", "देना", "लेना", "खोना", "ख़रीदना",
               "बेचना", "धन", "संपत्ति", "अमीर", "ग़रीब", "सोना",
               "चाँदी", "ख़ज़ाना", "चोरी", "भिक्षा", "दान", "ऋण"],
        "sa": ["धा", "दधाति", "दा", "ददाति", "ग्रह्", "गृह्णाति",
               "लभ्", "लभते", "हृ", "हरति", "धन", "विभूति",
               "संपद्", "रत्न", "सुवर्ण", "कोश", "दान", "भिक्षा",
               "dhaa", "dadhaati", "daa", "dadaati", "grah", "gRhNaati",
               "labh", "labhate", "hR", "harati", "dhana", "vibhuuti",
               "sampad", "ratna", "suvarNa", "kosha", "daana"],
    },
    "DOMINATION": {
        "hi": ["राजा", "रानी", "राज", "सत्ता", "शासन", "आदेश",
               "क़ानून", "दंड", "सिंहासन", "ताज", "प्रभु", "स्वामी",
               "सेवक", "दास", "अधिकार", "विजय", "साम्राज्य", "सम्राट"],
        "sa": ["राज्", "राजति", "शास्", "शास्ति", "ईश्", "ईष्टे",
               "राजन्", "राज्ञी", "साम्राज्य", "सिंहासन", "राज्य",
               "धर्म", "दण्ड", "न्याय", "प्रभु", "ईश्वर", "स्वामिन्",
               "raaj", "raajati", "shaas", "shaasti", "iish",
               "raajan", "saamraajya", "simhaasana", "raajya",
               "dharma", "daNDa", "nyaaya", "prabhu", "iishvara", "svaamin"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # EMOT atoms — emotional processes
    # ═══════════════════════════════════════════════════════════════════
    "SEEKING": {
        "hi": ["खोजना", "चाहना", "इच्छा", "आशा", "लालसा", "तलाश",
               "भूख", "प्यास", "कामना", "अभिलाषा", "उत्सुक",
               "माँगना", "ढूँढना", "प्रयास", "लक्ष्य", "साधना"],
        "sa": ["इष्", "इच्छति", "एष्", "एषति", "मृग्", "मृगयते",
               "काम", "इच्छा", "स्पृहा", "तृष्णा", "आशा",
               "अभिलाषा", "कामना", "एषणा", "साधना",
               "iSh", "ichChati", "eSh", "eShati", "mRg", "mRgayate",
               "kaama", "ichChaa", "spRhaa", "tRShNaa", "aashaa",
               "abhilaaSha", "kaamanaa", "saadhana"],
    },
    "FEAR": {
        "hi": ["डर", "भय", "डरना", "आतंक", "दहशत", "घबराना",
               "काँपना", "चिंता", "खौफ़", "त्रास", "भयानक",
               "डरावना", "भीत", "विभीषिका", "आशंका", "संत्रास"],
        "sa": ["भी", "बिभेति", "त्रस्", "त्रसति", "भय", "त्रास",
               "भीति", "आतंक", "संत्रास", "उद्वेग", "शंका",
               "विभीषिका", "भयानक", "भीत", "कम्प्",
               "bhii", "bibheti", "tras", "trasati", "bhaya",
               "bhiiti", "aatanka", "santaasa", "udvega", "shankaa",
               "vibhiiShikaa", "bhayanaka"],
    },
    "CARE": {
        "hi": ["प्रेम", "प्यार", "स्नेह", "दया", "करुणा", "सहायता",
               "रक्षा", "सेवा", "ममता", "वात्सल्य", "कोमल",
               "सांत्वना", "मित्रता", "अपनापन", "गले लगाना", "सहारा"],
        "sa": ["प्रेम", "स्निह्", "स्निह्यति", "रक्ष्", "रक्षति",
               "पा", "पाति", "दया", "करुणा", "अनुकम्पा",
               "वात्सल्य", "मैत्री", "स्नेह", "कृपा", "सेवा",
               "prema", "snih", "snihyati", "rakSh", "rakShati",
               "paa", "paati", "dayaa", "karuNaa", "anukampaa",
               "vaatsalya", "maitrii", "sneha", "kRpaa", "sevaa"],
    },
    "GRIEF": {
        "hi": ["दुख", "शोक", "रोना", "पीड़ा", "कष्ट", "विलाप",
               "आँसू", "तकलीफ़", "वेदना", "व्यथा", "ग़म",
               "मातम", "विरह", "संताप", "क्लेश", "विषाद"],
        "sa": ["शुच्", "शोचति", "रुद्", "रोदिति", "दुःख", "शोक",
               "वेदना", "व्यथा", "पीडा", "क्लेश", "विलाप",
               "अश्रु", "करुण", "विषाद", "संताप",
               "shuch", "shochati", "rud", "roditi", "duHkha", "shoka",
               "vedanaa", "vyathaa", "piiDaa", "klesha", "vilaapa",
               "ashru", "karuNa", "viShaada", "santaapa"],
    },
    "RAGE": {
        "hi": ["क्रोध", "गुस्सा", "आग", "प्रतिशोध", "घृणा", "रोष",
               "उग्र", "कोप", "प्रकोप", "क्रुद्ध", "जलना",
               "बदला", "आक्रोश", "प्रचंड", "उन्माद", "तामस"],
        "sa": ["क्रुध्", "क्रुध्यति", "कुप्", "कुप्यति", "क्रोध", "कोप",
               "रोष", "मन्यु", "प्रकोप", "अमर्ष", "प्रतिकार",
               "उग्र", "चण्ड", "प्रचण्ड", "क्रूर",
               "krudh", "krudhyati", "kup", "kupyati", "krodha", "kopa",
               "roSha", "manyu", "prakopa", "amarSha", "pratikaara",
               "ugra", "chaNDa", "prachaNDa", "kruura"],
    },
    "DISGUST": {
        "hi": ["घिन", "घृणा", "नफ़रत", "तिरस्कार", "अपमान",
               "गंदा", "सड़ा", "बदबू", "अशुद्ध", "वीभत्स",
               "जुगुप्सा", "विरक्ति", "ग्लानि", "कुत्सा", "निंदा"],
        "sa": ["जुगुप्स्", "जुगुप्सते", "निन्द्", "निन्दति",
               "जुगुप्सा", "घृणा", "वीभत्स", "अशुचि", "मलिन",
               "अमेध्य", "निन्दा", "कुत्सा", "ग्लानि", "विरक्ति",
               "jugups", "jugupsate", "nind", "nindati",
               "jugupsaa", "ghRNaa", "viibhatsa", "ashuchi",
               "malina", "amedhya", "nindaa", "kutsaa", "glaani"],
    },
    "PLAY": {
        "hi": ["खेलना", "हँसना", "ख़ुशी", "आनंद", "नाचना", "त्योहार",
               "गाना", "मज़ा", "हर्ष", "उल्लास", "रास", "लीला",
               "विनोद", "क्रीड़ा", "मनोरंजन", "उत्सव"],
        "sa": ["क्रीड्", "क्रीडति", "हस्", "हसति", "नृत्", "नृत्यति",
               "आनन्द", "हर्ष", "प्रमोद", "उल्लास", "रास",
               "लीला", "क्रीडा", "विनोद", "उत्सव",
               "kriiD", "kriiDati", "has", "hasati", "nRt", "nRtyati",
               "aananda", "harSha", "pramoda", "ullaasa", "raasa",
               "liilaa", "kriiDaa", "vinoda", "utsava"],
    },
    "TEDIUM": {
        "hi": ["ऊब", "थकान", "आलस्य", "सुस्ती", "उदासीन",
               "नीरस", "एकरस", "जड़", "निरुत्साह", "विरक्ति",
               "उबाऊ", "बेज़ार", "शिथिल", "मंद", "क्लांत"],
        "sa": ["खिद्", "खिद्यति", "ग्लै", "ग्लायति", "आलस्य",
               "जड", "तन्द्रा", "निद्रा", "शिथिल", "मन्द",
               "क्लान्त", "निरुत्साह", "विरक्ति", "खेद",
               "khid", "khidyati", "glai", "glaayati", "aalasya",
               "jaDa", "tandraa", "nidraa", "shithila", "manda",
               "klaanta", "nirutsaaha", "virakti", "kheda"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # ABS atoms — abstract structures
    # ═══════════════════════════════════════════════════════════════════
    "RELATION": {
        "hi": ["संबंध", "रिश्ता", "नाता", "बीच", "जुड़ाव",
               "बंधन", "कड़ी", "मेल", "योग", "साथ",
               "संपर्क", "सरोकार", "वास्ता", "लगाव", "अनुबंध"],
        "sa": ["सम्बन्ध", "योग", "बन्ध", "संयोग", "सम्पर्क",
               "अन्तर", "मध्य", "सह", "साहचर्य", "अनुबन्ध",
               "sambandha", "yoga", "bandha", "samyoga", "samparka",
               "antara", "madhya", "saha", "saahacharya", "anubandha"],
    },
    "STRUCTURE": {
        "hi": ["संरचना", "ढाँचा", "रूप", "व्यवस्था", "प्रणाली",
               "बनावट", "आकृति", "गठन", "ढंग", "क्रम",
               "तंत्र", "योजना", "रचना", "स्वरूप", "विन्यास"],
        "sa": ["संस्कार", "रचना", "विन्यास", "तन्त्र", "प्रणाली",
               "आकृति", "रूप", "स्वरूप", "व्यवस्था", "गठन",
               "sanskaara", "rachanaa", "vinyaasa", "tantra", "praNaalii",
               "aakRti", "ruupa", "svaruupa", "vyavasthaa", "gaThana"],
    },
    "ORDRE": {
        "hi": ["क्रम", "नियम", "विधि", "पंक्ति", "श्रेणी",
               "अनुशासन", "व्यवस्था", "विधान", "परंपरा",
               "क्रमबद्ध", "सुव्यवस्थित", "नियमावली", "पद्धति"],
        "sa": ["क्रम", "नियम", "विधि", "धर्म", "ऋत",
               "व्यवस्था", "अनुशासन", "शासन", "पद्धति",
               "krama", "niyama", "vidhi", "dharma", "Rta",
               "vyavasthaa", "anushaasana", "shaasana", "paddhati"],
    },
    "MESURE": {
        "hi": ["मापना", "माप", "गिनती", "संख्या", "वज़न",
               "लंबाई", "ऊँचाई", "गहराई", "दूरी", "मात्रा",
               "परिमाण", "आकार", "तौल", "अनुपात", "विस्तार"],
        "sa": ["मा", "मिमीते", "मान", "माना", "संख्या",
               "परिमाण", "मात्रा", "प्रमाण", "तुला",
               "maa", "mimiite", "maana", "maatraa", "sankhyaa",
               "parimaaNa", "pramaaNa", "tulaa", "maapana"],
    },
    "RÉCURRENCE": {
        "hi": ["दोहराव", "चक्र", "लय", "वापसी", "फिर",
               "बार-बार", "परंपरा", "ऋतु", "आवृत्ति",
               "पुनरावृत्ति", "नियमित", "आवर्तन", "चक्रीय"],
        "sa": ["आवृत्ति", "पुनर्", "पुनः", "चक्र", "कल्प",
               "युग", "ऋतु", "काल", "संसार", "आवर्तन",
               "aavRtti", "punar", "punaH", "chakra", "kalpa",
               "yuga", "Rtu", "kaala", "samsaara", "aavartana"],
    },
    "INVARIANCE": {
        "hi": ["अटल", "स्थिर", "शाश्वत", "सनातन", "अमर",
               "अचल", "ध्रुव", "नित्य", "अविनाशी", "अक्षय",
               "चिरंतन", "सदा", "हमेशा", "अमिट", "अपरिवर्तनीय"],
        "sa": ["नित्य", "शाश्वत", "सनातन", "अमृत", "अक्षर",
               "ध्रुव", "अविनाशिन्", "अव्यय", "अचल", "स्थिर",
               "nitya", "shaashvata", "sanaatana", "amRta", "akShara",
               "dhruva", "avinaashin", "avyaya", "achala", "sthira"],
    },
    "DUALITÉ": {
        "hi": ["विपरीत", "जोड़ा", "दोहरा", "द्वंद्व", "विरोध",
               "दो", "दर्पण", "विरोधाभास", "उलटा", "द्विविध",
               "संतुलन", "द्वैत", "युग्म", "प्रतिबिंब"],
        "sa": ["द्वन्द्व", "द्वय", "द्वैत", "युग्म", "विरोध",
               "प्रतिपक्ष", "अद्वैत", "द्वि", "परस्पर",
               "dvandva", "dvaya", "dvaita", "yugma", "virodha",
               "pratipakSha", "advaita", "dvi", "paraspara"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # ENT atoms — entities (objects, substances)
    # ═══════════════════════════════════════════════════════════════════
    "CHOSE": {
        "hi": ["चीज़", "वस्तु", "पदार्थ", "सामान", "तत्त्व",
               "द्रव्य", "माल", "सामग्री", "उपकरण", "कुछ"],
        "sa": ["वस्तु", "पदार्थ", "द्रव्य", "तत्त्व", "भूत",
               "अर्थ", "विषय", "रूप",
               "vastu", "padaartha", "dravya", "tattva", "bhuuta",
               "artha", "viShaya"],
    },
    "AGENT": {
        "hi": ["मनुष्य", "व्यक्ति", "आदमी", "औरत", "बच्चा",
               "लोग", "जन", "नर", "नारी", "पुरुष",
               "स्त्री", "कोई", "नागरिक", "प्राणी", "मानव"],
        "sa": ["पुरुष", "नर", "नारी", "स्त्री", "मनुष्य",
               "जन", "प्राणिन्", "जीव", "देव", "मानव",
               "puruSha", "nara", "naarii", "strii", "manuShya",
               "jana", "praaNin", "jiiva", "deva", "maanava"],
    },
    "CORPS": {
        "hi": ["शरीर", "सिर", "हाथ", "आँख", "हृदय", "पैर",
               "बाँह", "मुँह", "चेहरा", "ख़ून", "हड्डी",
               "त्वचा", "बाल", "उँगली", "पीठ", "छाती", "कंधा"],
        "sa": ["शरीर", "देह", "शिरस्", "हस्त", "नेत्र", "हृदय",
               "पाद", "बाहु", "मुख", "वदन", "रक्त", "अस्थि",
               "त्वच्", "केश", "अङ्गुलि", "पृष्ठ", "वक्षस्",
               "shariira", "deha", "shiras", "hasta", "hRdaya",
               "paada", "baahu", "mukha", "vadana", "rakta", "asthi",
               "kesh", "anguli", "vakShas"],
    },
    "LIEU": {
        "hi": ["जगह", "घर", "कमरा", "शहर", "देश", "दुनिया",
               "गाँव", "बाग़", "जंगल", "पहाड़", "समुद्र", "नदी",
               "सड़क", "रास्ता", "मैदान", "ज़मीन", "आकाश", "पृथ्वी"],
        "sa": ["स्थान", "गृह", "नगर", "देश", "लोक", "जगत्",
               "ग्राम", "वन", "पर्वत", "सागर", "नदी", "मार्ग",
               "क्षेत्र", "भूमि", "आकाश", "पृथिवी", "स्वर्ग",
               "sthaana", "gRha", "nagara", "desha", "loka", "jagat",
               "graama", "vana", "parvata", "saagara", "nadii", "maarga",
               "kShetra", "bhuumi", "aakaasha", "pRthivii", "svarga"],
    },
    "MATIÈRE": {
        "hi": ["पानी", "आग", "पत्थर", "लकड़ी", "लोहा", "सोना",
               "चाँदी", "मिट्टी", "हवा", "धूल", "रेत",
               "काँच", "चमड़ा", "कपड़ा", "ऊन", "ताँबा"],
        "sa": ["जल", "अग्नि", "पाषाण", "काष्ठ", "अयस्", "सुवर्ण",
               "रजत", "मृत्तिका", "वायु", "पृथिवी", "आप्",
               "तेजस्", "आकाश", "लोह", "तामस",
               "jala", "agni", "paaShaaNa", "kaaShTha", "ayas", "suvarNa",
               "rajata", "mRttikaa", "vaayu", "aap",
               "tejas", "loha"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # QUAL atoms — qualitative (properties, attributes)
    # ═══════════════════════════════════════════════════════════════════
    "BON": {
        "hi": ["अच्छा", "सुंदर", "भला", "शुभ", "मंगल", "उत्तम",
               "श्रेष्ठ", "पवित्र", "शुद्ध", "सत्", "धर्म",
               "सद्गुण", "कल्याण", "प्रसन्न", "शांत", "दिव्य"],
        "sa": ["शुभ", "सुन्दर", "मङ्गल", "कल्याण", "श्रेष्ठ",
               "उत्तम", "पवित्र", "शुद्ध", "पुण्य", "धर्म",
               "सत्", "दिव्य", "प्रसन्न", "सु",
               "shubha", "sundara", "mangala", "kalyaaNa", "shreShTha",
               "uttama", "pavitra", "shuddha", "puNya",
               "divya", "prasanna", "su"],
    },
    "GRAND": {
        "hi": ["बड़ा", "लंबा", "ऊँचा", "विशाल", "विस्तृत",
               "महान", "भव्य", "विराट", "प्रचंड", "अथाह",
               "अपार", "महा", "बृहत्", "गहन", "प्रबल"],
        "sa": ["महत्", "बृहत्", "विशाल", "विराट", "उच्च",
               "दीर्घ", "महान्", "विस्तृत", "प्रचण्ड",
               "mahat", "bRhat", "vishaala", "viraaTa", "uchcha",
               "diirgha", "mahaan", "vistRta", "prachaNDa"],
    },
    "VRAI": {
        "hi": ["सच", "सत्य", "असली", "वास्तविक", "ईमानदार",
               "सच्चा", "विश्वसनीय", "यथार्थ", "प्रामाणिक",
               "निष्कपट", "खरा", "निश्चित", "प्रमाणित"],
        "sa": ["सत्य", "ऋत", "तथ्य", "यथार्थ", "प्रमाण",
               "निश्चय", "सत्", "आप्त", "प्रामाणिक",
               "satya", "Rta", "tathya", "yathaarta", "pramaaNa",
               "nishchaya", "sat", "aapta", "pramaaNika"],
    },
    "INTENSE": {
        "hi": ["बहुत", "अत्यंत", "अति", "प्रचंड", "भीषण",
               "ज़बरदस्त", "प्रबल", "तीव्र", "उग्र", "घोर",
               "भयंकर", "असाधारण", "विलक्षण", "अत्यधिक"],
        "sa": ["अति", "परम", "अत्यन्त", "तीव्र", "प्रचण्ड",
               "उग्र", "घोर", "भीषण", "महा", "सुतराम्",
               "ati", "parama", "atyanta", "tiivra", "prachaNDa",
               "ugra", "ghora", "bhiiShaNa", "mahaa", "sutaraam"],
    },
    "ANCIEN": {
        "hi": ["पुराना", "प्राचीन", "पूर्वज", "अतीत", "बीता",
               "सदियों", "परंपरा", "विरासत", "पुरातन", "सनातन",
               "पुरखे", "पहले", "कभी", "पुरावशेष", "इतिहास"],
        "sa": ["पुरातन", "प्राचीन", "पूर्व", "पुराण", "सनातन",
               "पूर्वज", "पितामह", "चिर", "प्राक्", "पुरा",
               "puraatana", "prachiina", "puurva", "puraaNa", "sanaatana",
               "puurvaja", "pitaamaha", "chira", "praak", "puraa"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Supplementary structural/function words for Indic languages
# ═══════════════════════════════════════════════════════════════════════════════

INDIC_NEGATION_WORDS = {
    "hi": ["नहीं", "न", "मत", "ना", "कभी नहीं", "कुछ नहीं",
           "कोई नहीं", "बिना", "बिल्कुल नहीं"],
    "sa": ["न", "ना", "मा", "अ", "अन्", "नहि",
           "na", "naa", "maa", "a", "an", "nahi"],
}

INDIC_QUANTIFIER_WORDS = {
    "hi": ["बहुत", "कम", "सब", "हर", "कुछ", "कई",
           "अधिक", "थोड़ा", "सारा", "ज़्यादा", "पूरा",
           "अनेक", "काफ़ी", "समस्त"],
    "sa": ["बहु", "अल्प", "सर्व", "प्रत्येक", "अनेक",
           "अधिक", "किञ्चित्", "समस्त", "सकल",
           "bahu", "alpa", "sarva", "pratyeka", "aneka",
           "adhika", "ki~nchit", "samasta", "sakala"],
}

INDIC_MODIFIER_WORDS = {
    "hi": ["बहुत", "अत्यंत", "काफ़ी", "ख़ासकर", "बिल्कुल",
           "पूरी तरह", "वाक़ई", "सचमुच", "अवश्य",
           "निश्चित रूप से", "अतिशय", "परम"],
    "sa": ["अति", "परम", "सुतराम्", "अत्यन्त", "एव",
           "खलु", "वै", "तु", "हि", "किल",
           "ati", "parama", "sutaraam", "atyanta", "eva",
           "khalu", "vai", "tu", "hi", "kila"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE PROFILES for Hindi and Sanskrit
# ═══════════════════════════════════════════════════════════════════════════════

INDIC_LANGUAGE_PROFILES = {
    "hi": {
        "lang_name": "Hindi",
        "word_order": "SOV",
        "morphological_richness": "high",
        "case_system": True,
        "grammatical_gender": True,
        "agglutinative": True,
        "avg_sentence_length_preference": 16.0,
        "subordination_tendency": "medium",
        "formality_levels": "3-tier",
        "notes": "SOV with postpositions. Devanagari script with spaces between words. "
                 "Ergative-absolutive alignment in perfective aspect. "
                 "Gender (M/F), number, case. Hindi-Urdu continuum.",
        "determiners": {"यह", "वह", "ये", "वे", "इस", "उस",
                        "मेरा", "मेरी", "तेरा", "तेरी", "उसका", "उसकी",
                        "हमारा", "हमारी", "कोई", "कुछ", "हर", "सब",
                        "एक", "कई", "बहुत", "थोड़ा"},
        "prepositions": set(),  # Hindi uses postpositions, not prepositions
        "conjunctions": {"और", "लेकिन", "या", "कि", "क्योंकि", "मगर",
                         "पर", "तो", "जब", "अगर", "चाहे", "हालाँकि",
                         "परंतु", "इसलिए", "ताकि", "जबकि", "फिर भी"},
        "pronouns": {"मैं", "मुझे", "मेरा", "तू", "तुझे", "तुम", "तुम्हें",
                     "आप", "आपको", "वह", "उसे", "यह", "इसे",
                     "हम", "हमें", "वे", "उन्हें", "कौन", "क्या",
                     "जो", "कोई", "कुछ", "अपना", "ख़ुद"},
        "auxiliaries": {"है", "हैं", "था", "थी", "थे", "थीं",
                        "होगा", "होगी", "होंगे", "हो", "हुआ", "हुई",
                        "रहा", "रही", "रहे", "सकता", "सकती", "सकते",
                        "चाहिए", "पड़ता", "पड़ती", "लगता", "लगती"},
        "negations": {"नहीं", "न", "मत", "ना", "बिना", "बिल्कुल नहीं"},
        "past_markers": {"था", "थी", "थे", "थीं", "हुआ", "गया"},
        "present_markers": {"है", "हैं", "हो", "रहा", "रही"},
        "future_markers": {"होगा", "होगी", "होंगे", "गा", "गी", "गे"},
        "formal_markers": {"कृपया", "महोदय", "श्रीमान", "श्रीमती"},
        "archaic_markers": {"वचन", "कहत", "करत", "मोहि", "तोहि",
                            "तुम्हरे", "हमरे", "ताहि"},
        "literary_markers": {"हाय", "अहो", "अरे", "वाह", "हे"},
        "temporal_connectors": {"फिर", "फिर भी", "उसके बाद", "पहले",
                                "जब", "तब", "अचानक", "अंत में",
                                "तुरंत", "जल्दी", "धीरे-धीरे"},
        "causal_connectors": {"क्योंकि", "इसलिए", "अतः", "चूँकि",
                              "के कारण", "की वजह से"},
        "adversative_connectors": {"लेकिन", "मगर", "परंतु", "फिर भी",
                                   "हालाँकि", "बावजूद"},
        "additive_connectors": {"और", "भी", "साथ ही", "इसके अलावा",
                                "तथा"},
        "measurement_system": "metric",
        "cultural_food": {"रोटी", "चावल", "दाल", "चाय", "दूध",
                          "घी", "पानी", "मिठाई"},
    },
    "sa": {
        "lang_name": "Sanskrit",
        "word_order": "SOV",
        "morphological_richness": "very_high",
        "case_system": True,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 20.0,
        "subordination_tendency": "very_high",
        "formality_levels": "3-tier",
        "notes": "8-case system (nominative through locative + vocative). "
                 "3 numbers (sg/du/pl), 3 genders (M/F/N). Rich sandhi system. "
                 "10 verbal classes (gaṇa). Free word order in verse. "
                 "Pāṇini's Aṣṭādhyāyī defines its grammar with ~4000 sūtras. "
                 "Gutenberg pg9000 uses ITRANS romanization, not Devanagari.",
        "determiners": {"एतद्", "तद्", "इदम्", "अयम्", "असौ",
                        "एषः", "सः", "सा", "तत्",
                        # ITRANS
                        "etad", "tad", "idam", "ayam", "asau",
                        "eShaH", "saH", "saa", "tat"},
        "prepositions": set(),  # Sanskrit uses case endings, not prepositions
        "conjunctions": {"च", "तु", "वा", "किन्तु", "परन्तु",
                         "अथ", "तथा", "एव", "अपि", "यदि",
                         "यदा", "तदा", "यतः", "ततः", "अतः",
                         # ITRANS
                         "cha", "tu", "vaa", "kintu", "parantu",
                         "atha", "tathaa", "eva", "api", "yadi",
                         "yadaa", "tadaa", "yataH", "tataH", "ataH"},
        "pronouns": {"अहम्", "माम्", "त्वम्", "त्वाम्", "सः", "सा", "तत्",
                     "वयम्", "युष्माकम्", "ते", "एषः", "एषा",
                     "कः", "का", "किम्", "यः", "या", "यत्",
                     "आत्मन्", "स्वयम्",
                     # ITRANS
                     "aham", "maam", "tvam", "tvaam", "vayam",
                     "kaH", "kaa", "kim", "yaH", "yaa", "yat",
                     "aatman", "svayam"},
        "auxiliaries": {"अस्ति", "स्ति", "भवति", "आसीत्",
                        # ITRANS
                        "asti", "sti", "bhavati", "aasiit"},
        "negations": {"न", "ना", "मा", "अ", "अन्",
                      # ITRANS
                      "na", "naa", "maa"},
        "past_markers": {"अकरोत्", "अभवत्"},
        "present_markers": {"अस्ति", "भवति", "करोति"},
        "future_markers": {"भविष्यति", "करिष्यति"},
        "formal_markers": set(),
        "archaic_markers": set(),  # Sanskrit IS archaic
        "literary_markers": {"अहो", "हा", "धिक्", "साधु", "स्वस्ति",
                             # ITRANS
                             "aho", "haa", "dhik", "saadhu", "svasti"},
        "temporal_connectors": {"ततः", "तदा", "पूर्वम्", "पश्चात्",
                                "यदा", "अथ", "इदानीम्", "अन्ते",
                                # ITRANS
                                "tataH", "tadaa", "puurvam", "pashchaat",
                                "yadaa", "atha", "idaaniim", "ante"},
        "causal_connectors": {"यतः", "अतः", "तस्मात्", "हि",
                              # ITRANS
                              "yataH", "ataH", "tasmaat", "hi"},
        "adversative_connectors": {"किन्तु", "परन्तु", "तु", "अपि",
                                   # ITRANS
                                   "kintu", "parantu", "api"},
        "additive_connectors": {"च", "अपि", "तथा", "एव",
                                # ITRANS
                                "cha", "api", "tathaa", "eva"},
        "measurement_system": "traditional",
        "cultural_food": {"अन्न", "घृत", "पयस्", "मधु", "सोम",
                          # ITRANS
                          "anna", "ghRta", "payas", "madhu", "soma"},
    },
}


def merge_indic_keywords(atom_keywords):
    """Merge INDIC_KEYWORDS into the main ATOM_KEYWORDS dictionary.

    Called at module load time by gutenberg_multilingual_validator.py.
    Modifies atom_keywords in-place.
    """
    for atom, lang_dict in INDIC_KEYWORDS.items():
        if atom not in atom_keywords:
            continue
        for lang, keywords in lang_dict.items():
            if lang not in atom_keywords[atom]:
                atom_keywords[atom][lang] = keywords[:]
            else:
                existing = set(atom_keywords[atom][lang])
                atom_keywords[atom][lang].extend(
                    kw for kw in keywords if kw not in existing
                )
