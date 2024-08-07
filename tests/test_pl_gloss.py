from unittest import TestCase

from wikitextprocessor import Wtp
from wiktextract.config import WiktionaryConfig
from wiktextract.extractor.pl.page import parse_page
from wiktextract.wxr_context import WiktextractContext


class TestPlGloss(TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.wxr = WiktextractContext(
            Wtp(lang_code="pl"),
            WiktionaryConfig(
                dump_file_lang_code="pl",
                capture_language_codes=None,
            ),
        )

    def tearDown(self) -> None:
        self.wxr.wtp.close_db_conn()

    def test_gloss(self):
        self.wxr.wtp.add_page(
            "Szablon:język polski",
            10,
            '<span class="lang-code primary-lang-code lang-code-pl" id="pl">[[Słownik języka polskiego|język polski]]</span>[[Kategoria:polski (indeks)]]',
        )
        self.wxr.wtp.add_page("Szablon:kynol", 10, "kynol.")
        self.wxr.wtp.add_page(
            "Szablon:wikipedia",
            10,
            '<span><templatestyles src="skrót/styles.css" /><span class="short-container short-no-comma-next">[[Aneks:Skróty używane w Wikisłowniku#Z|<span class="short-wrapper" title="zobacz" data-expanded="zobacz"><span class="short-content">zob.</span></span>]]</span> '
            "też"
            " [[w:Dog|dog]] w Wikipedii</span>",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "dog",
                """== dog ({{język polski}}) ==
===znaczenia===
''rzeczownik, rodzaj męskozwierzęcy''
: (1.1) {{kynol}} [[nazwa]] [[rasa|rasy]] [[pies|psa]]; {{wikipedia}}""",
            ),
            [
                {
                    "categories": ["polski (indeks)"],
                    "lang": "język polski",
                    "lang_code": "pl",
                    "senses": [
                        {
                            "glosses": ["nazwa rasy psa"],
                            "topics": ["cynology"],
                            "sense_index": "1.1",
                        }
                    ],
                    "pos": "noun",
                    "pos_text": "rzeczownik",
                    "tags": ["masculine", "animate"],
                    "word": "dog",
                }
            ],
        )

    def test_abbr(self):
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>[[Kategoria:angielski (indeks)]]',
        )
        self.wxr.wtp.add_page("Szablon:kynol", 10, "kynol.")
        self.assertEqual(
            parse_page(
                self.wxr,
                "AYPI",
                """== AYPI ({{język angielski}}) ==
===znaczenia===
''skrótowiec''
: (1.1) = [[and|And]] [[your|Your]] [[point|Point]] [[is|Is]]? → [[co|Co]] [[chcieć|chciałeś]] [[przez]] [[to]] [[powiedzieć|powiedzieć]]?""",
            ),
            [
                {
                    "categories": ["angielski (indeks)"],
                    "lang": "język angielski",
                    "lang_code": "en",
                    "senses": [
                        {
                            "glosses": [
                                "And Your Point Is? → Co chciałeś przez to powiedzieć?"
                            ],
                            "sense_index": "1.1",
                        }
                    ],
                    "pos": "abbrev",
                    "pos_text": "skrótowiec",
                    "tags": ["abbreviation"],
                    "word": "AYPI",
                }
            ],
        )

    def test_example(self):
        self.wxr.wtp.add_page("Szablon:język angielski", 10, "język angielski")
        page_data = parse_page(
            self.wxr,
            "dream",
            """== dream ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (2.1) [[sen]]
===przykłady===
: (2.1) ''[[passionately|Passionately]] [[enamor]]ed [[of]] [[this]] [[shadow]] [[of]] [[a]] [[dream]]''<ref>Washington Irving</ref> → [[gorąco|Gorąco]] [[zakochany]] [[w]] [[cień|cieniu]] [[ze]] '''[[sen|snów]]'''""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "Passionately enamored of this shadow of a dream",
                        "ref": "Washington Irving",
                        "translation": "Gorąco zakochany w cieniu ze snów",
                    }
                ],
                "glosses": ["sen"],
                "sense_index": "2.1",
            },
        )

    def test_examples_across_different_pos_sections(self):
        self.wxr.wtp.add_page(
            "Szablon:język angielski",
            10,
            '<span class="lang-code primary-lang-code lang-code-en" id="en">[[Słownik języka angielskiego|język angielski]]</span>',
        )
        self.wxr.wtp.add_page("Szablon:zool", 10, "zool.")
        page_data = parse_page(
            self.wxr,
            "dog",
            """== dog ({{język angielski}}) ==
===znaczenia===
''rzeczownik policzalny''
: (1.1) {{zool}} [[pies]]
''czasownik przechodni''
: (3.1) [[ścigać]], [[śledzić]]
===przykłady===
: (1.1) ''[[it|It]] [[be|is]] [[say|said]] [[that]] [[a]] [[dog]] [[is]] [[a]] [[human]][['s]] [[good|best]] [[friend]].'' → [[mówić|Mówi]] [[się]], [[że]] '''[[pies]]''' [[być|jest]] [[dobry|najlepszym]] [[przyjaciel]]em [[człowiek]]a.
: (3.1) ''[[trouble|Trouble]] [[dog]]ged [[his]] [[every]] [[step]].'' → [[kłopot|Kłopoty]] '''[[dosięgać|dosięgały]]''' [[on|go]] [[na]] [[każdy]]m [[krok]]u.""",
        )
        self.assertEqual(
            page_data[0]["senses"][0],
            {
                "examples": [
                    {
                        "text": "It is said that a dog is a human's best friend.",
                        "translation": "Mówi się, że pies jest najlepszym przyjacielem człowieka.",
                    }
                ],
                "glosses": ["pies"],
                "raw_tags": ["zool."],
                "sense_index": "1.1",
            },
        )
        self.assertEqual(
            page_data[1]["senses"][0],
            {
                "examples": [
                    {
                        "text": "Trouble dogged his every step.",
                        "translation": "Kłopoty dosięgały go na każdym kroku.",
                    }
                ],
                "glosses": ["ścigać, śledzić"],
                "sense_index": "3.1",
            },
        )

    def test_form_of(self):
        self.wxr.wtp.add_page(
            "Szablon:język szwedzki",
            10,
            '<span class="lang-code primary-lang-code lang-code-sv" id="sv">[[Słownik języka szwedzkiego|język szwedzki]]</span>[[Kategoria:szwedzki (formy fleksyjne)]]',
        )
        self.wxr.wtp.add_page(
            "Szablon:forma czasownika",
            10,
            "<i>czasownik, forma fleksyjna</i>[[Kategoria:Formy czasowników szwedzkich]]",
        )
        self.wxr.wtp.add_page(
            "Szablon:szw-forma czas-przesz",
            10,
            "''czas przeszły ([[preteritum#sv|preteritum]]) od'' [[dö#sv|dö]]",
        )
        self.assertEqual(
            parse_page(
                self.wxr,
                "dog",
                """== dog ({{język szwedzki}}) ==
===znaczenia===
''{{forma czasownika|sv}}''
: (1.1) {{szw-forma czas-przesz|dö}}""",
            ),
            [
                {
                    "categories": [
                        "szwedzki (formy fleksyjne)",
                        "Formy czasowników szwedzkich",
                    ],
                    "lang": "język szwedzki",
                    "lang_code": "sv",
                    "senses": [
                        {
                            "form_of": [{"word": "dö"}],
                            "glosses": ["czas przeszły (preteritum) od dö"],
                            "sense_index": "1.1",
                        }
                    ],
                    "tags": ["form-of"],
                    "pos": "verb",
                    "pos_text": "czasownik",
                    "word": "dog",
                }
            ],
        )
