POS_DATA = {
    "명사": {"pos": "noun"},
    "형용사": {"pos": "adj"},
    "대명사": {"pos": "pron"},
    "수사": {"pos": "num"},
    "동사": {"pos": "verb"},
    "관용구": {"pos": "phrase", "tags": ["idiomatic"]},
    "기호": {"pos": "symbol"},
    "접미사": {"pos": "suffix", "tags": ["morpheme"]},
    "접두사": {"pos": "prefix", "tags": ["morpheme"]},
    "의미": {"pos": "unknown"},
    "타동사": {"pos": "verb", "tags": ["transitive"]},
    "종별사": {"pos": "counter"},
    "감탄사": {"pos": "intj"},
    "조동사": {"pos": "verb", "tags": ["auxiliary"]},
    "부사": {"pos": "adv"},
    "조사": {"pos": "particle"},
    "어근": {"pos": "root", "tags": ["morpheme"]},
    "용어": {"pos": "name"},
    "자동사": {"pos": "verb", "tags": ["intransitive"]},
    "속담": {"pos": "proverb"},
    "접속사": {"pos": "conj"},
    "관형사": {"pos": "det"},
    "전치사": {"pos": "prep"},
    "형용사 활용형": {"pos": "adv"},
    "형태소": {"pos": "character"},
    "어간": {"pos": "stem"},
    "어미": {"pos": "suffix", "tags": ["morpheme"]},
    "의존 명사": {"pos": "noun", "tags": ["dependent"]},
    "품사": {"pos": "unknown"},
    "후치사": {"pos": "postp"},
    "연어": {"pos": "phrase", "tags": ["idiomatic"]},
    "동사 활용형": {"pos": "verb", "tags": ["form-of"]},
    "재귀동사": {"pos": "verb", "tags": ["reflexive"]},
    "보조형용사": {"pos": "adj", "tags": ["auxiliary"]},
    "고유명사": {"pos": "name"},
    "고유 명사": {"pos": "name"},
    "개사": {"pos": "unknown"},
    "간지": {"pos": "unknown"},
    "이곳에 품사를 입력하세요": {"pos": "unknown"},
    "여기에 품사를 적어주세요": {"pos": "unknown"},
    "い형용사": {"pos": "adj"},
    "な형용사": {"pos": "adj"},
    "관사": {"pos": "article"},
    "격조사": {"pos": "particle"},
    "명사구": {"pos": "noun"},
    "병음": {"pos": "romanization"},
    "양사": {"pos": "classifier"},
    "어소": {"pos": "unknown", "tags": ["morpheme"]},
    "문자": {"pos": "character", "tags": ["letter"]},
    "알파벳": {"pos": "character", "tags": ["letter"]},
    "동사구": {"pos": "phrase"},
    "약자": {"pos": "abbrev", "tags": ["abbreviation"]},
    "방위사": {"pos": "noun"},
    "보조사": {"pos": "unknown", "tags": ["completive"]},  # accessory word
    "사투리": {"pos": "unknown", "tags": ["dialectal"]},
    "부사구": {"pos": "adv"},
    "모음": {"pos": "character", "tags": ["letter"]},
    "보어": {"pos": "unknown", "tags": ["completive"]},
    "옛말": {"pos": "proverb", "tags": ["archaic"]},
    "자/타동사": {"pos": "verb", "tags": ["transitive", "intransitive"]},
    "음소": {"pos": "letter", "tags": ["phoneme"]},
    "연체사": {"pos": "adnominal"},
    "한자": {"pos": "character", "tags": ["Hanja"]},
    "학명": {"pos": "name"},
    "이태동사": {"pos": "verb"},
    "어구": {"pos": "phrase"},
}

LINKAGE_SECTIONS = {
    "속담": "proverbs",
    "합성어": "derived",
    "파생어": "derived",
    "관련 어휘": "related",
    "유의어": "synonyms",
    "반의어": "antonyms",
    "관용구": "proverbs",
    "반대말": "antonyms",
    "비슷한 말": "synonyms",
    "어구": "derived",
    "관련 어구": "derived",
    "관련 표현": "related",
    "같이 보기": "related",
    "복합어": "derived",
    "관련 단어": "related",
    "동의어": "synonyms",
    "관용 표현": "idioms",
    "관련 기호": "related",
    "관려 어휘": "related",
    "단어": "derived",
    "관용어": "idioms",
    "관련어휘": "related",
    "문화어": "synonyms",
    "비표준어": "synonyms",
    "숙어": "idioms",
    "하위어": "hyponyms",
    "참고": "related",
}
